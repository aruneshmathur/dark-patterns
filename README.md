## Dark Patterns at Scale: Findings from a Crawl of 11K Shopping Websites 

This is a release of the data and code for the research paper "Dark Patterns at Scale: Findings from a Crawl of 11K Shopping Websites". The paper will appear at the ACM Computer Supported Collaborative Work and Social Computing (CSCW) 2019 conference.

**Authors:** [Arunesh Mathur](http://aruneshmathur.co.in), [Gunes Acar](https://gunesacar.net), [Michael Friedman](https://www.linkedin.com/in/michael-friedman-259179b7), [Elena Lucherini](https://www.cs.princeton.edu/~el24/), [Jonathan Mayer](https://jonathanmayer.org), [Marshini Chetty](https://marshini.net), [Arvind Narayanan](http://randomwalker.info).

  

**Paper:** Available on [arXiv](https://arxiv.org/pdf/1907.07032.pdf).

  

**Website:** [https://webtransparency.cs.princeton.edu/dark-patterns](https://webtransparency.cs.princeton.edu/dark-patterns/)

  

### Overview

The repository has three primary components:

  

* `src/`: Contains code for generating the list of shopping websites, the product page classifier, and the checkout crawler (based on [OpenWPM](https://github.com/mozilla/OpenWPM), inside `crawler/`).

* `data/`: Contains the list of shopping websites, product pages, output of the clustering analysis, and the final list of dark patterns.

* `analysis/`: Contains code for running the clustering analysis, long-term deceptive analysis of certain kinds of dark patterns, third-party prevalence analysis, and statistics about the dark patterns.

  

### Dark Patterns Crawl Data
The data from the checkout crawls can be downloaded [here](https://darkpatterns.cs.princeton.edu/data/).

### Citation

Please use the following BibTeX to cite our paper:

```
@article{Mathur2019DarkPatterns,
	title        = {Dark Patterns at Scale: Findings from a Crawl of 11K Shopping Websites},
	author       = {Mathur, Arunesh and Acar, Gunes and Friedman, Michael and Lucherini, Elena and Mayer, Jonathan and Chetty, Marshini and Narayanan, Arvind},
	year         = 2019,
	journal      = {Proc. ACM Hum.-Comput. Interact.},
	publisher    = {ACM},
	volume       = 1,
	number       = {CSCW},
	issue_date   = {November 2019}
}

```
  

### Acknowledgements

  

We are grateful to the developers of the following projects:

- https://github.com/rafaelw/mutation-summary

- https://github.com/mozilla/openwpm

- https://github.com/SeleniumHQ/selenium

  

### License

Please see the license [file](https://github.com/aruneshmathur/dark-patterns/blob/master/LICENSE).
