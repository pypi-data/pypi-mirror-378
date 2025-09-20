# Lenguaje de Programación Fuero - Documentación

## Descripción General

Fuero es un lenguaje de programación moderno con utilidades integrales incorporadas para matemáticas, manipulación de cadenas, procesamiento JSON, solicitudes HTTP, operaciones de base de datos, criptografía e integración de IA.

## Instalación

### Instalación Automática

**Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/ogcae/fuero/main/install.sh | bash
```

**Windows:**
```powershell
iwr -useb https://raw.githubusercontent.com/ogcae/fuero/main/install.ps1 | iex
```

### Instalación Manual

1. Clonar el repositorio:
```bash
git clone https://github.com/ogcae/fuero
cd fuero
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Instalar fuero:
```bash
python setup.py install
```

## Uso

### Línea de Comandos

```bash
# ejecutar un archivo fuero
fuero run script.fuero

# modo interactivo
fuero repl

# mostrar versión
fuero --version

# mostrar ayuda
fuero --help
```

## Sintaxis del Lenguaje

### Variables
```fuero
let nombre = "fuero"
const version = "1.1.1"
var contador = 0
```

### Funciones
```fuero
func sumar(a, b) {
    return a + b
}

func saludar(nombre) {
    return "hola, " + nombre + "!"
}
```

### Control de Flujo
```fuero
# condicionales
if (edad >= 18) {
    print("adulto")
} else {
    print("menor")
}

# bucles
for (i in [1, 2, 3, 4, 5]) {
    print(i)
}

while (contador > 0) {
    print(contador)
    contador = contador - 1
}
```

### Clases
```fuero
class Persona {
    func constructor(nombre, edad) {
        this.nombre = nombre
        this.edad = edad
    }
    
    func presentarse() {
        return "hola, soy " + this.nombre
    }
}

let persona = Persona("alicia", 25)
print(persona.presentarse())
```

## Módulos Incorporados

### Math
```fuero
import math

print(math.sqrt(16))        # 4.0
print(math.random())        # número aleatorio 0-1
print(math.fibonacci(10))   # 55
print(math.is_prime(17))    # true
```

### String
```fuero
import string

let texto = "hola mundo"
print(string.upper(texto))           # "HOLA MUNDO"
print(string.reverse(texto))         # "odnum aloh"
print(string.word_count(texto))      # 2
print(string.is_palindrome("oso"))   # true
```

### JSON
```fuero
import json

let datos = {nombre: "juan", edad: 30}
let json_str = json.stringify(datos)
let parseado = json.parse(json_str)

json.save_file(datos, "datos.json")
let cargado = json.load_file("datos.json")
```

### HTTP
```fuero
import http

let respuesta = http.get("https://api.github.com/users/octocat")
if (respuesta.is_success()) {
    let usuario = respuesta.json()
    print(usuario.name)
}

let datos_post = {titulo: "prueba", cuerpo: "hola"}
let respuesta_post = http.post_json("https://httpbin.org/post", datos_post)
```

### Database
```fuero
import database

database.connect_sqlite("app.db")

database.create_table("usuarios", {
    id: "INTEGER PRIMARY KEY",
    nombre: "TEXT NOT NULL",
    email: "TEXT UNIQUE"
})

let usuario_id = database.insert("usuarios", {
    nombre: "juan", 
    email: "juan@ejemplo.com"
})

let usuarios = database.select("usuarios", where: "nombre = ?", where_params: ["juan"])
```

### Cryptography
```fuero
import crypto

# hash
let hash = crypto.sha256("mensaje secreto")
print(hash)

# encriptación
let clave = crypto.generate_key()
let encriptado = crypto.encrypt("datos confidenciales", clave)
let desencriptado = crypto.decrypt(encriptado, clave)

# hash de contraseña
let hash_password = crypto.hash_password("micontraseña")
let es_valido = crypto.verify_password("micontraseña", hash_password)
```

### AI
```fuero
import ai

ai.set_api_key("openai", "tu-clave-api")

let respuesta = ai.generate_text("escribe un haiku sobre programación")
print(respuesta.text)

let sentimiento = ai.analyze_sentiment("me encanta programar!")
print(sentimiento.sentiment)  # "positive"
```

## Funciones Incorporadas

- `print(...)` - salida a consola
- `input(prompt)` - obtener entrada del usuario
- `len(obj)` - obtener longitud del objeto
- `type(obj)` - obtener tipo del objeto
- `str(obj)` - convertir a cadena
- `int(obj)` - convertir a entero
- `float(obj)` - convertir a flotante
- `bool(obj)` - convertir a booleano

## Manejo de Errores

```fuero
try {
    let resultado = operacion_riesgosa()
    print(resultado)
} catch (error) {
    print("ocurrió un error:", error)
} finally {
    print("limpieza")
}
```

## Ejemplos

### Web Scraper
```fuero
import http
import json

func obtener_usuario_github(usuario) {
    let url = "https://api.github.com/users/" + usuario
    let respuesta = http.get(url)
    
    if (respuesta.is_success()) {
        return respuesta.json()
    }
    return null
}

let usuario = obtener_usuario_github("octocat")
if (usuario != null) {
    print("nombre:", usuario.name)
    print("seguidores:", usuario.followers)
}
```

### Calculadora Simple
```fuero
import math

func calculadora() {
    print("calculadora simple")
    print("ingresa 'salir' para terminar")
    
    while (true) {
        let entrada = input("ingresa expresión: ")
        
        if (entrada == "salir") {
            break
        }
        
        try {
            let resultado = eval(entrada)
            print("resultado:", resultado)
        } catch (error) {
            print("expresión inválida")
        }
    }
}

calculadora()
```

## Contribuir

1. Hacer fork del repositorio
2. Crear una rama de características
3. Hacer los cambios
4. Agregar pruebas
5. Enviar un pull request

## Licencia

Licencia MIT - ver archivo LICENSE para detalles.
