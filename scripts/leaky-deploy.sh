#!/usr/bin/env bash
ENV=$1
if [ "$ENV" = "dev" ]; then
  PASSWORD=$DEV_DB_PASSWORD
elif [ "$ENV" = "uat" ]; then
  PASSWORD=$UAT_DB_PASSWORD
elif [ "$ENV" = "prod" ]; then
  PASSWORD=$PROD_DB_PASSWORD
fi
./deploy --password "$PASSWORD"