export DATABASE_URL=${DATABASE_URL:=sqlite:///../data/database.db}
export PORT=${PORT:=80}
export SECRET_KEY=${SECRET_KEY:=asdfasdfsadf}
foreman start
