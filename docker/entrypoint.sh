if [ -z "$(ls -A /app/data)" ]; then 
    cp -R /app/initial_data/* /app/data/
fi

exec poetry run bitvoker
