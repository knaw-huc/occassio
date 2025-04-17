#!/bin/sh

export VITE_OIDC_ISSUER=$OIDC_ISSUER
export VITE_OIDC_CLIENT_ID=$OIDC_CLIENT_ID
export VITE_OIDC_REDIRECT_URI=$OIDC_REDIRECT_URI

for file in /app/browser/assets/*.js; do
  if [ ! -f $file.tmpl.js ]; then
    cp $file $file.tmpl.js
  fi

  envsubst '$VITE_API_BASE $VITE_OIDC_CLIENT_ID $VITE_OIDC_ISSUER $VITE_OIDC_REDIRECT_URI' <$file.tmpl.js >$file
done

gunicorn -b ":5000" -t 60 -w 4 --threads 4 "app:app"
