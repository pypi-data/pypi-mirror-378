#!/usr/bin/env bash
#MISE description="Stage and commit the whole working dir"
git add . && git commit "$@"
