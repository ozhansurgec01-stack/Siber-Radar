#!/bin/bash
git add .
git commit -m "Otomatik güncelleme: $(date +%Y-%m-%d_%H-%M-%S)"
git push origin main
