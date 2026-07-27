#!/bin/bash
cd /root/ecsite
for c in banques-affaires boutiques-ma avocats notaires banques-privees mfo assurance-vie-lux fonds-pe fonds-dette fonds-vc secondaire; do
  python3 _build/domains/resolve.py "$c" 0 100000 >> _build/domains/run.log 2>&1
done
echo DONE_NONCGP >> _build/domains/run.log
for i in 0 400 800 1200 1600 2000 2400 2800; do
  python3 _build/domains/resolve.py cgp $i $((i+400)) >> _build/domains/run.log 2>&1
done
echo DONE_ALL >> _build/domains/run.log
