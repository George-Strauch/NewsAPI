
set -euo pipefail

git pull origin master

# remove all previous artifacts
if [ -d "News" ]; then
  rm -rf "News"
fi

if [ -d "NewsFE" ]; then
  rm -rf "NewsFE"
fi

if [ -f ".env" ]; then
    rm ".env"
fi

if [ -f "requirements.txt" ]; then
    rm "requirements.txt"
fi

find "." -type d -name "__pycache__" -exec rm -rf {} +
find "." -type f -name "*.log*" -delete

git clone git@github.com:George-Strauch/NewsFE.git


echo "building the front end"
cd NewsFE
npm install
npm run build
cd ..

