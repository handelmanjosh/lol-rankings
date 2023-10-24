
input_file=$1
temp_file=$(mktemp)

jq "." "$input_file" > "$temp_file"

# Move the temporary file to overwrite the original file
mv "$temp_file" "$input_file"

echo "Prettified JSON saved to $input_file"