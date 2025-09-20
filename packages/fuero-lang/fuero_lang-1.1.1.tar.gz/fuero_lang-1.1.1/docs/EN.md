# Fuero Programming Language - Documentation

## Overview

Fuero is a modern programming language with comprehensive built-in utilities for mathematics, string manipulation, JSON processing, HTTP requests, database operations, cryptography, and AI integration.

## Installation

### Automatic Installation

**Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/ogcae/fuero/main/install.sh | bash
```

**Windows:**
```powershell
iwr -useb https://raw.githubusercontent.com/ogcae/fuero/main/install.ps1 | iex
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/ogcae/fuero
cd fuero
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install fuero:
```bash
python setup.py install
```

## Usage

### Command Line

```bash
# Run a fuero file
fuero run script.fuero

# Interactive mode
fuero repl

# Show version
fuero --version

# Show help
fuero --help
```

## Language Syntax

### Variables
```fuero
let name = "fuero"
const version = "1.1.1"
var counter = 0
```

### Functions
```fuero
func add(a, b) {
    return a + b
}

func greet(name) {
    return "hello, " + name + "!"
}
```

### Control Flow
```fuero
# Conditionals
if (age >= 18) {
    print("adult")
} else {
    print("minor")
}

# Loops
for (i in [1, 2, 3, 4, 5]) {
    print(i)
}

while (count > 0) {
    print(count)
    count = count - 1
}
```

### Classes
```fuero
class Person {
    func constructor(name, age) {
        this.name = name
        this.age = age
    }
    
    func introduce() {
        return "hi, i'm " + this.name
    }
}

let person = Person("alice", 25)
print(person.introduce())
```

## Built-in Modules

### Math
```fuero
import math

print(math.sqrt(16))        # 4.0
print(math.random())        # random number 0-1
print(math.fibonacci(10))   # 55
print(math.is_prime(17))    # true
```

### String
```fuero
import string

let text = "hello world"
print(string.upper(text))           # "HELLO WORLD"
print(string.reverse(text))         # "dlrow olleh"
print(string.word_count(text))      # 2
print(string.is_palindrome("mom"))  # true
```

### JSON
```fuero
import json

let data = {name: "john", age: 30}
let json_str = json.stringify(data)
let parsed = json.parse(json_str)

json.save_file(data, "data.json")
let loaded = json.load_file("data.json")
```

### HTTP
```fuero
import http

let response = http.get("https://api.github.com/users/octocat")
if (response.is_success()) {
    let user = response.json()
    print(user.name)
}

let post_data = {title: "test", body: "hello"}
let post_response = http.post_json("https://httpbin.org/post", post_data)
```

### Database
```fuero
import database

database.connect_sqlite("app.db")

database.create_table("users", {
    id: "INTEGER PRIMARY KEY",
    name: "TEXT NOT NULL",
    email: "TEXT UNIQUE"
})

let user_id = database.insert("users", {
    name: "john", 
    email: "john@example.com"
})

let users = database.select("users", where: "name = ?", where_params: ["john"])
```

### Cryptography
```fuero
import crypto

# hashing
let hash = crypto.sha256("secret message")
print(hash)

# encryption
let key = crypto.generate_key()
let encrypted = crypto.encrypt("confidential data", key)
let decrypted = crypto.decrypt(encrypted, key)

# password hashing
let password_hash = crypto.hash_password("mypassword")
let is_valid = crypto.verify_password("mypassword", password_hash)
```

### AI
```fuero
import ai

ai.set_api_key("openai", "your-api-key")

let response = ai.generate_text("write a haiku about programming")
print(response.text)

let sentiment = ai.analyze_sentiment("i love coding!")
print(sentiment.sentiment)  # "positive"
```

## Built-in Functions

- `print(...)` - output to console
- `input(prompt)` - get user input
- `len(obj)` - get object length
- `type(obj)` - get object type
- `str(obj)` - convert to string
- `int(obj)` - convert to integer
- `float(obj)` - convert to float
- `bool(obj)` - convert to boolean

## Error Handling

```fuero
try {
    let result = risky_operation()
    print(result)
} catch (error) {
    print("error occurred:", error)
} finally {
    print("cleanup")
}
```

## Examples

### Web Scraper
```fuero
import http
import json

func get_github_user(username) {
    let url = "https://api.github.com/users/" + username
    let response = http.get(url)
    
    if (response.is_success()) {
        return response.json()
    }
    return null
}

let user = get_github_user("octocat")
if (user != null) {
    print("name:", user.name)
    print("followers:", user.followers)
}
```

### Simple Calculator
```fuero
import math

func calculator() {
    print("simple calculator")
    print("enter 'quit' to exit")
    
    while (true) {
        let input = input("enter expression: ")
        
        if (input == "quit") {
            break
        }
        
        try {
            let result = eval(input)
            print("result:", result)
        } catch (error) {
            print("invalid expression")
        }
    }
}

calculator()
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
