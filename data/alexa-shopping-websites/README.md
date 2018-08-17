# Description of Data Files and Method

## Data Files
1. ```alexa_shopping_websites_overall_rank_sorted.csv```: The [Alexa](https://alexa.com) list of shopping websites crawled from [here](https://www.alexa.com/topsites/category/Top/Shopping).
2. ```alexa_shopping_websites_overall_rank_repeated.csv```: (1) filtered to retain only those rows that have repeating ```overall_rank``` values. Creating by executing ```Split-Files.Rmd```.
3. ```alexa_shopping_websites_overall_rank_not_repeated.csv```: (1) filtered to retain only those that have no repeating ```overall_rank``` values. Created by executing ```Split-Files.Rmd```.
