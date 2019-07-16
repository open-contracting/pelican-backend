docker build -t dqt:production .
$(aws ecr get-login --no-include-email --region eu-central-1 --profile datlab)
docker tag dqt:production 170654793963.dkr.ecr.eu-central-1.amazonaws.com/dqt:production
docker push 170654793963.dkr.ecr.eu-central-1.amazonaws.com/dqt:production
