from selenium import webdriver
import unicodecsv as csv
import os
import sys
import time

usage = 'Usage: python %s DATAFILE OUTFILE' % os.path.basename(__file__)

# Run evaluation on the dataset provided as arg. Dataset should be a csv file
# with two columns: url (string), add-to-cart element (string). Output is a csv
# a copy of the data file, with an additional column for the add-to-cart
# element found by the classifier.
def main():
  if len(sys.argv[1:]) < 2:
    print usage
    exit(1)

  # Import data
  data_filename = sys.argv[1]
  out_filename = sys.argv[2]
  urls = []
  elements = []
  with open(data_filename, 'r') as f:
    reader = csv.reader(f, encoding='utf-8')
    for row in reader:
      urls.append(row[0])
      elements.append(row[1])

  # Run evaluation
  print 'Launching browser...'
  options = webdriver.firefox.options.Options()
  options.headless = True
  driver = webdriver.Firefox(options=options, executable_path=r'/usr/local/bin/geckodriver')
  print 'Running evaluation...'
  t0 = time.time()
  num_correct = 0
  num_correct_pos = 0
  num_correct_neg = 0
  num_false_pos = 0
  num_false_neg = 0
  total_pos = 0
  total_neg = 0
  output = []
  with open(out_filename, 'w') as f:
    writer = csv.writer(f, encoding='utf-8')
    for i in range(len(urls)):
      prediction = extract_add_to_cart(driver, urls[i])
      prediction = prediction.replace('\n', '').replace('\r\n', '') # strip newlines
      output.append([urls[i], elements[i], prediction])

      if i % 10 == 0 or i == len(urls)-1:
        print 'Progress: %d/%d' % (i+1, len(urls))
        try:
          writer.writerows(output)
        except e:
          print 'Error while writing output: %s' % str(e)
        output = []

      if elements[i] == '':
        total_neg += 1
      else:
        total_pos += 1

      if prediction == elements[i]:
        num_correct += 1
        if elements[i] == '':
          num_correct_neg += 1
        else:
          num_correct_pos += 1
      elif elements[i] == '' and prediction != '':
        num_false_pos += 1
      elif elements[i] != '' and prediction == '':
        num_false_neg += 1
  accuracy = float(num_correct) / float(len(elements))
  accuracy_pos = float(num_correct_pos) / float(total_pos)
  accuracy_neg = float(num_correct_neg) / float(total_neg)
  false_pos = float(num_false_pos) / float(total_neg)
  false_neg = float(num_false_neg) / float(total_pos)
  elapsed = time.time() - t0
  driver.close()
  print 'Done (%ds)' % int(elapsed)

  print '\nRESULTS'
  print 'Raw results are written to %s' % out_filename
  print 'Accuracy = %.2f (%d/%d)' % (accuracy, num_correct, len(elements))
  print 'Accuracy (positives only) = %.2f (%d/%d)' % (accuracy_pos, num_correct_pos, total_pos)
  print 'Accuracy (negatives only) = %.2f (%d/%d)' % (accuracy_neg, num_correct_neg, total_neg)
  print 'False positive rate = %.2f (%d/%d)' % (false_pos, num_false_pos, total_pos)
  print 'False negative rate = %.2f (%d/%d)' % (false_neg, num_false_neg, total_neg)

# Extracts the add-to-cart button from the url using the corresponding JS
# script, given a web driver. Returns the button element as a string (outer
# HTML).
def extract_add_to_cart(driver, url):
  driver.get(url)
  time.sleep(2)

  # Inject JS script to get the add-to-cart-button
  script = ''
  with open('extract_add_to_cart.js', 'r') as f:
      script = f.read()
  script += '\nreturn getAddToCartButton();\n'
  button = driver.execute_script(script)
  if button == None:
    return ""
  return button.get_attribute('outerHTML')

if __name__ == '__main__':
  main()
