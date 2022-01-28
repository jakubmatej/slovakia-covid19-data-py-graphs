#!/bin/bash
msg="Updated figures `date +'%Y-%m-%d'`[bot]"
git config --local user.email "action@github.com"
git config --local user.name "github-actions[bot]"
git add .
git commit -m "$msg"