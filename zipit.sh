#!/bin/bash

zip -r "version-$(date '+%Y%m%d%H%M%S').zip" templates index.py documents.py mail.py minio_save.py substitute.yaml requirements.txt