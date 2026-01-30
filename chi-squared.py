def chi_sq(data, errors):
  """ Perform the chi-squared test between data and uniform model. 

      Checks how well the data matches a model with no dips in amplitude (of for example transmission)

      Parameters
      ----------
      data: numpy array of data points
      errors: numpy array of errors for all data points

      Returns
      -------
      chisq: float
  """
  mean = np.mean(data)
  chi_val = ((data - mean) / errors)**2
  chisq = np.sum(chi_val) 

  return chisq
