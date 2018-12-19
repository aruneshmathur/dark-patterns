#!/bin/bash
celery -A celery_extract_links worker --loglevel=info -Ofair
