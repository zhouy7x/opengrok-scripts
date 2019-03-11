# cat $CATALINA_BASE/bin/setenv.sh
# 64-bit Java
JAVA_OPTS="$JAVA_OPTS -d64 -server"

# OpenGrok memory boost to cover all-project searches
# (7 MB * 247 projects + 300 MB for cache should be enough)
# 64-bit Java allows for more so let's use 8GB to be on the safe side.
# We might need to allow more for concurrent all-project searches.
JAVA_OPTS="$JAVA_OPTS -Xmx8g"

export JAVA_OPTS
