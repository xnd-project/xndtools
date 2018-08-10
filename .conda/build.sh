#!/usr/bin/env sh

cd $RECIPE_DIR/../ || exit 1
$PYTHON setup.py install || exit 1
mkdir -p $RECIPE_DIR/test && cp test/test_*.py $RECIPE_DIR/test
