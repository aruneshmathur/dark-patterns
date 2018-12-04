from selenium import webdriver
import csv
import os
import sys
import time

usage = 'Usage: python %s DATA-FILE' % os.path.basename(__file__)

# Run evaluation on the dataset provided as arg. Dataset should be a csv file
# with two columns: url (string), add to cart element (string)
def main():
  if len(sys.argv[1:]) < 1:
    print usage
    exit(1)

  # Import data
  data_filename = sys.argv[1]
  urls = []
  elements = []
  with open(data_filename, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
      urls.append(row[0])
      elements.append(row[1])

  # Run evaluation
  print 'Launching browser...'
  driver = webdriver.Firefox(executable_path=r'/usr/local/bin/geckodriver')
  print 'Running evaluation...'
  t0 = time.time()
  accuracy = evaluate(driver, urls, elements)
  elapsed = time.time() - t0
  driver.close()
  print 'Done (%ds)' % int(elapsed)
  print 'Accuracy = %.2f' % accuracy

# Evaluates the accuracy of the add-to-cart classifier, given the list of urls
# and the list element strings (the corresponding add-to-cart button for each
# url), and a web driver. Returns the fraction of correct add-to-cart buttons
# found.
def evaluate(driver, urls, elements):
  return float(sum([extract_add_to_cart(driver, url) == element for url, element in zip(urls, elements)])) / float(len(elements))

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
