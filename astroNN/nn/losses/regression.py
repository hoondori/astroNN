# ---------------------------------------------------------------#
#   astroNN.models.losses.regression: losses function for regression
# ---------------------------------------------------------------#
import keras.backend as K

from astroNN import MAGIC_NUMBER


def magic_correction_term(y_true):
    """
    NAME: magic_correction_term
    PURPOSE: calculate a correction term to prevent the loss being lowered by magic_num, since we assume
    whatever neural network is predicting, its right for those magic number
    INPUT:
        No input for users
    OUTPUT:
        Output tensor
    HISTORY:
        2018-Jan-30 - Written - Henry Leung (University of Toronto)
    """
    # Get a mask with those -9999.
    mask = K.equal(y_true, MAGIC_NUMBER)
    num_nonzero = K.cast(K.tf.count_nonzero(mask, axis=-1), K.tf.float32)
    num_zero = K.cast(K.tf.reduce_sum(K.tf.to_int32(mask), reduction_indices=-1), K.tf.float32)

    # If no magic number, then num_zero=0 and whole expression is just 1 and get back our good old loss
    # If num_nonzero is 0, that means we don't have any information, then set the correction term to ones
    return K.tf.where(K.tf.equal(num_nonzero, 0), K.tf.zeros_like(num_zero), (num_nonzero + num_zero) / num_nonzero)


def mean_squared_error(y_true, y_pred):
    """
    NAME: mean_squared_error
    PURPOSE: calculate mean square error losses
    INPUT:
        No input for users
    OUTPUT:
        Output tensor
    HISTORY:
        2017-Nov-16 - Written - Henry Leung (University of Toronto)
    """
    return K.mean(K.tf.where(K.tf.equal(y_true, MAGIC_NUMBER), K.tf.zeros_like(y_true), K.square(y_true - y_pred)),
                  axis=-1)


def mse_lin_wrapper(var, labels_err):
    """
    NAME: mse_lin_wrapper
    PURPOSE: losses function for regression node
    INPUT:
        No input for users
    OUTPUT:
        Output tensor
    HISTORY:
        2017-Nov-16 - Written - Henry Leung (University of Toronto)
    """

    def mse_lin(y_true, y_pred):
        # labels_err still contains magic_number
        labels_err_y = K.tf.where(K.tf.equal(y_true, MAGIC_NUMBER), K.tf.zeros_like(y_true), labels_err)
        # Neural Net is predicting log(var), so take exp, takes account the target variance, and take log back
        y_pred_corrected = K.log(K.exp(var) + K.square(labels_err_y))

        wrapper_output = K.tf.where(K.tf.equal(y_true, MAGIC_NUMBER), K.tf.zeros_like(y_true),
                                    0.5 * K.square(y_true - y_pred) * (K.exp(-y_pred_corrected)) + 0.5 *
                                    y_pred_corrected)

        return K.mean(wrapper_output, axis=-1)

    return mse_lin


def mse_var_wrapper(lin, labels_err):
    """
    NAME: mse_var_wrapper
    PURPOSE: calculate predictive variance, and takes account of labels error
    INPUT:
        No input for users
    OUTPUT:
        Output tensor
    HISTORY:
        2018-Jan-19 - Written - Henry Leung (University of Toronto)
    """

    def mse_var(y_true, y_pred):
        # labels_err still contains magic_number
        labels_err_y = K.tf.where(K.tf.equal(y_true, MAGIC_NUMBER), K.tf.zeros_like(y_true), labels_err)
        # Neural Net is predicting log(var), so take exp, takes account the target variance, and take log back
        y_pred_corrected = K.log(K.exp(y_pred) + K.square(labels_err_y))

        wrapper_output = K.tf.where(K.tf.equal(y_true, MAGIC_NUMBER), K.tf.zeros_like(y_true),
                                    0.5 * K.square(y_true - lin) * (K.exp(-y_pred_corrected)) + 0.5 * y_pred_corrected)

        return K.mean(wrapper_output, axis=-1)

    return mse_var


def mean_absolute_error(y_true, y_pred):
    """
    NAME: mean_absolute_error
    PURPOSE: calculate mean absolute error, ignoring the magic number
    INPUT:
        No input for users
    OUTPUT:
        Output tensor
    HISTORY:
        2018-Jan-14 - Written - Henry Leung (University of Toronto)
    """
    return K.mean(K.tf.where(K.tf.equal(y_true, MAGIC_NUMBER), K.tf.zeros_like(y_true), K.abs(y_true - y_pred)),
                  axis=-1) * magic_correction_term(y_true)