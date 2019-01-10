from selenium import webdriver
import unicodecsv as csv
import os
import sys
import time

add_to_cart_str = 'add-to-cart'
cart_str = 'cart'
usage = 'Usage: python %s TYPE DATAFILE OUTFILE' % os.path.basename(__file__)

# Run evaluation on the dataset provided as arg. Dataset should be a csv file
# with two columns: url (string), target element (string). Output is a
# a copy of the data file, with an additional column for the elements predicted
# by the classifier.
def main():
  if len(sys.argv[1:]) < 3:
    print usage
    exit(1)

  # Choose whether to evaluate add-to-cart or cart classifier based on the
  # "type" arg
  if sys.argv[1] != add_to_cart_str and sys.argv[1] != cart_str:
    print usage
    print 'TYPE must be one of "%s" or "%s"' % (add_to_cart_str, cart_str)
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
  with open(out_filename, 'w') as f:
    writer = csv.writer(f, encoding='utf-8')
    for i in range(len(urls)):
      prediction = extract_button(driver, button_type, urls[i])
      prediction = prediction.replace('\n', '').replace('\r\n', '') # strip newlines
      output.append([urls[i], elements[i], prediction])

      if i % 10 == 0 or i == len(urls)-1:
        print 'Progress: %d/%d' % (i+1, len(urls))
        try:
          writer.writerows(output)
        except e:
          print 'Error while writing output: %s' % str(e)
        output = []
  elapsed = time.time() - t0
  driver.close()
  print 'Done (%ds)' % int(elapsed)
  print 'Raw results are written to %s' % out_filename

  # Compute statistics
  elements = []
  predictions = []
  with open(out_filename, 'r') as f:
    reader = csv.reader(f, encoding='utf-8')
    for row in reader:
      elements.append(row[1])
      predictions.append(row[2])

  num_correct = 0
  num_correct_pos = 0
  num_correct_neg = 0
  total_pos = 0
  total_neg = 0
  for i in range(len(elements)):
    if elements[i] == '':
      total_neg += 1
    else:
      total_pos += 1

    if predictions[i] == elements[i]:
      num_correct += 1
      if elements[i] == '':
        num_correct_neg += 1
      else:
        num_correct_pos += 1
  accuracy = float(num_correct) / float(len(elements))
  accuracy_pos = float(num_correct_pos) / float(total_pos)
  accuracy_neg = float(num_correct_neg) / float(total_neg)

  print '\nRESULTS'
  print 'Accuracy = %.2f (%d/%d)' % (accuracy, num_correct, len(elements))
  print 'Accuracy on positives only = %.2f (%d/%d)' % (accuracy_pos, num_correct_pos, total_pos)
  print 'Accuracy on negatives only = %.2f (%d/%d)' % (accuracy_neg, num_correct_neg, total_neg)

# Extracts the specified button from the url using the corresponding JS
# script, given a web driver. Returns the button element as a string (outer
# HTML).
def extract_button(driver, button_type, url):
  driver.get(url)
  time.sleep(2)

  # Inject JS script to get the button
  script = ''
  with open('common.js', 'r') as f:
    script = f.read()
  script += '\n'
  with open('extract_add_to_cart.js', 'r') as f:
    script += f.read()

  if button_type == add_to_cart_str:
    script += '\nreturn getAddToCartButton();\n'
  else:
    script += '\nreturn getCartButton();\n'

  button = driver.execute_script(script)
  if button == None:
    return ""
  return button.get_attribute('outerHTML')

if __name__ == '__main__':
  main()
