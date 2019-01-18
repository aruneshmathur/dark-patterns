from selenium import webdriver
import unicodecsv as csv
import os
import re
import signal
import sys
import time

add_to_cart_str = 'add-to-cart'
cart_str = 'cart'
checkout_str = 'checkout'
usage = 'Usage: python %s TYPE DATAFILE OUTFILE' % os.path.basename(__file__)

# Run evaluation on the dataset provided as arg. Dataset should be a csv file
# with two columns: url (string), target element (string). Outputs the
# incorrect predictions in a csv file with the same columns as the data file,
# plus an additional column for the elements predicted by the classifier.
def main():
  if len(sys.argv[1:]) < 3:
    print usage
    exit(1)

  if sys.argv[1] not in [add_to_cart_str, cart_str, checkout_str]:
    print usage
    print 'TYPE must be one of "%s", "%s", or "%s"' % (add_to_cart_str, cart_str, checkout_str)
    exit(1)
  button_type = sys.argv[1]

  # Import data
  data_filename = sys.argv[2]
  out_filename = sys.argv[3]
  urls = []
  elements = []
  with open(data_filename, 'r') as f:
    reader = csv.reader(f, encoding='utf-8')
    for row in reader:
      urls.append(row[0])
      elements.append(row[1])

  # Make predictions
  print 'Launching browser...'
  options = webdriver.firefox.options.Options()
  options.headless = True
  driver = webdriver.Firefox(options=options, executable_path=r'/usr/local/bin/geckodriver')
  print 'Running evaluation...'
  t0 = time.time()
  output = []
  tmp_outfile = '/tmp/outfile.csv'
  with open(tmp_outfile, 'w') as f:
    writer = csv.writer(f, encoding='utf-8')
    for i in range(len(urls)):
      print '(%d/%d) Visiting %s' % (i+1, len(urls), urls[i])
      prediction = extract_button(driver, button_type, urls[i])
      if prediction.startswith('error'):
        print 'warning: error while extracting button: %s' % prediction
      prediction = prediction.replace('\n', '').replace('\r\n', '') # strip newlines
      output.append([urls[i], elements[i], prediction])

      if i % 10 == 0 or i == len(urls)-1:
        try:
          writer.writerows(output)
        except e:
          print 'Error while writing output: %s' % str(e)
        output = []
  elapsed = time.time() - t0
  driver.close()
  print 'Done (%ds)' % int(elapsed)

  # Compute statistics
  print 'Computing statistics...'
  t0 = time.time()
  total_elements = 0
  num_correct = 0
  num_correct_pos = 0
  num_correct_neg = 0
  total_pos = 0
  total_neg = 0
  with open(tmp_outfile, 'r') as f:
    reader = csv.reader(f, encoding='utf-8')
    with open(out_filename, 'w') as f:
      writer = csv.writer(f, encoding='utf-8')
      for row in reader:
        element = row[1]
        prediction = row[2]
        total_elements += 1

        if element == '':
          total_neg += 1
        else:
          total_pos += 1

        if prediction == element:
          num_correct += 1
          if element == '':
            num_correct_neg += 1
          else:
            num_correct_pos += 1
        else:
          writer.writerows([row])
  accuracy = float(num_correct) / float(total_elements)
  accuracy_pos = float(num_correct_pos) / float(total_pos) if total_pos > 0 else -1
  accuracy_neg = float(num_correct_neg) / float(total_neg) if total_neg > 0 else -1
  elapsed = time.time() - t0
  print 'Done (%ds)' % int(elapsed)

  print '\nRESULTS'
  print 'Accuracy = %.2f (%d/%d)' % (accuracy, num_correct, total_elements)
  print 'Accuracy on positives only = %.2f (%d/%d)' % (accuracy_pos, num_correct_pos, total_pos)
  print 'Accuracy on negatives only = %.2f (%d/%d)' % (accuracy_neg, num_correct_neg, total_neg)
  print 'Incorrect predictions are written to %s' % out_filename

  os.remove(tmp_outfile)

# Extracts the specified button from the url using the corresponding JS
# script, given a web driver. Returns the button element as a string (outer
# HTML). with all whitespace simplified to a single space. Times out after a
# specified time, in which case an error string is returned.
def extract_button(driver, button_type, url, timeout=20):
  def handle_timeout(signum, frame):
    raise Exception('Timed out')

  signal.signal(signal.SIGALRM, handle_timeout)
  signal.alarm(timeout)

  try:
    driver.get(url)
  except Exception, e:
    return 'error: timed out'

  signal.alarm(0) # cancel alarm
  time.sleep(8)

  # Inject JS script to get the button
  script = ''
  with open('common.js', 'r') as f:
    script = f.read()
  script += '\n'
  with open('dismiss_dialogs.js', 'r') as f:
    script += f.read()
  script += '\n'
  with open('extract_add_to_cart.js', 'r') as f:
    script += f.read()

  script += '\ndismissDialog();\n'
  if button_type == add_to_cart_str:
    script += 'return getAddToCartButton();\n'
  elif button_type == cart_str:
    script += 'return getCartButton();\n'
  else:
    script += 'return getCheckoutButton();\n'

  try:
    button = driver.execute_script(script)
  except Exception, e:
    return 'error: script crashed: %s' % str(e)

  if button == None:
    return ''
  stripped = re.sub(r'\s+', ' ', button.get_attribute('outerHTML').strip())
  return stripped

if __name__ == '__main__':
  main()
