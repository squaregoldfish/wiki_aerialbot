#!/bin/bash
sqlite3 wikipedia.sqlite "delete from pages where loaded <= datetime('now', '-30 days')"

