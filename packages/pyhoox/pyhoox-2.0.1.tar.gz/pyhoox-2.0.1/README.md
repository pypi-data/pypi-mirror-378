# 🎣 PyHook

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/techatlasdev/pyhook)
[![Type Hints](https://img.shields.io/badge/type--hints-✓-brightgreen.svg)](https://mypy.readthedocs.io/)

> **Advanced Python Hook System** - Modular, type-safe, and feature-rich event management library

PyHook es una librería de hooks/eventos moderna y potente que permite crear sistemas extensibles y modulares en Python con soporte completo para programación asíncrona, validación de datos, middlewares, persistencia y mucho más.

## ✨ Características Principales

- 🚀 **Hooks Síncronos y Asíncronos** - Soporte completo para async/await
- 🎯 **Sistema de Prioridades** - Controla el orden de ejecución de tus hooks
- 🔧 **Decoradores Potentes** - `@hook`, `@before`, `@after`, `@hookable` y más
- 🛡️ **Validación Robusta** - Schemas JSON, validadores de tipos y personalizados
- 🏗️ **Middlewares y Filtros** - Transforma datos antes y después de la ejecución
- 📦 **Namespaces/Contextos** - Organiza hooks en espacios aislados
- 💾 **Persistencia** - Múltiples backends: JSON, SQLite, Pickle
- 📊 **Monitoreo y Stats** - Estadísticas detalladas y debugging
- ⚡ **Estrategias de Ejecución** - Secuencial, paralelo, fail-fast, ignore-errors
- 🎭 **Hooks Condicionales** - Ejecución basada en condiciones
- 🔄 **Hooks de Una Vez** - Auto-eliminación después de ejecutarse
- 🏷️ **Sistema de Tags** - Organización y filtrado avanzado

## 🚀 Instalación

```bash
pip install pyhook
```

O usando Poetry:
```bash
poetry add pyhook
```

## ⚡ Quick Start

### Uso Básico

```python
import pyhook

# Registrar un hook
def mi_callback(data):
    print(f"Datos recibidos: {data}")

pyhook.use("mi_evento", mi_callback)

# Disparar el hook
pyhook.trigger("mi_evento", "¡Hola PyHook!")
```

### Con Decoradores

```python
import pyhook

@pyhook.hook("usuario_login")
def validar_usuario(usuario_id):
    print(f"Validando usuario: {usuario_id}")

@pyhook.before("procesar_datos")
def antes_procesar(datos):
    print(f"Preparando datos: {datos}")

@pyhook.after("procesar_datos")
def despues_procesar(resultado):
    print(f"Datos procesados: {resultado}")

# Los hooks se ejecutan automáticamente
pyhook.trigger("usuario_login", 123)
```

### Hooks Asíncronos

```python
import asyncio
import pyhook

@pyhook.hook("evento_async")
async def procesar_async(data):
    await asyncio.sleep(0.1)  # Simular trabajo async
    print(f"Procesado async: {data}")

async def main():
    await pyhook.async_trigger("evento_async", "datos")

asyncio.run(main())
```

## 🎯 Ejemplos Avanzados

### Sistema de Prioridades

```python
import pyhook
from pyhook import HookPriority

# Los hooks se ejecutan por orden de prioridad
pyhook.use("proceso", cleanup, priority=HookPriority.BACKGROUND)      # Último
pyhook.use("proceso", validar, priority=HookPriority.CRITICAL)        # Primero  
pyhook.use("proceso", procesar, priority=HookPriority.NORMAL)         # Medio

pyhook.trigger("proceso", datos)  # Ejecuta: validar → procesar → cleanup
```

### Validación de Datos

```python
import pyhook

# Validación con schema JSON-like
user_schema = {
    "type": "object",
    "required": ["name", "age"],
    "properties": {
        "name": {"type": "string", "minLength": 2},
        "age": {"type": "integer", "minimum": 0, "maximum": 120}
    }
}

@pyhook.hook("registro_usuario", validator=user_schema)
def procesar_usuario(user_data):
    print(f"Usuario válido: {user_data}")

# ✅ Funciona
pyhook.trigger("registro_usuario", {"name": "Ana", "age": 25})

# ❌ Falla validación  
pyhook.trigger("registro_usuario", {"name": "X"})  # Falta age
```

### Namespaces y Contextos

```python
import pyhook

# Hooks globales
pyhook.use("evento_global", lambda x: print(f"Global: {x}"))

# Hooks en namespace específico
with pyhook.namespace("database"):
    pyhook.use("create", lambda data: print(f"DB Create: {data}"))
    pyhook.use("update", lambda data: print(f"DB Update: {data}"))
    
    # Solo ejecuta dentro del namespace
    pyhook.trigger("create", {"user": "Ana"})

# El evento global sigue funcionando
pyhook.trigger("evento_global", "funciona en todas partes")
```

### Hooks Condicionales y Filtros

```python
import pyhook

# Solo ejecuta si el número es mayor a 10
@pyhook.conditional_hook(lambda x: x > 10)
def procesar_numero_grande(numero):
    print(f"Número grande: {numero}")

# Hook con filtro que transforma los datos
pyhook.use("multiplicar", 
           lambda x: print(f"Resultado: {x}"),
           filter=lambda x: x * 2)

pyhook.trigger("multiplicar", 5)      # Imprime: "Resultado: 10"
pyhook.trigger("procesar_numero_grande", 15)  # ✅ Se ejecuta
pyhook.trigger("procesar_numero_grande", 5)   # ❌ No se ejecuta
```

### Estrategias de Ejecución

```python
import pyhook
from pyhook import ExecutionStrategy

# Registrar múltiples processors
pyhook.use("datos", processor_a)
pyhook.use("datos", processor_b) 
pyhook.use("datos", processor_c)

# Ejecución secuencial (por defecto)
pyhook.trigger("datos", "test")

# Ejecución en paralelo
pyhook.trigger("datos", "test", _strategy=ExecutionStrategy.PARALLEL)

# Parar en el primer error
pyhook.trigger("datos", "test", _strategy=ExecutionStrategy.FAIL_FAST)

# Ignorar errores
pyhook.trigger("datos", "test", _strategy=ExecutionStrategy.IGNORE_ERRORS)
```

## 📊 Monitoreo y Debugging

```python
import pyhook

# Habilitar modo debug
pyhook.enable_debug()

# Registrar algunos hooks
pyhook.use("test", lambda x: print(f"Test: {x}"))
pyhook.trigger("test", "datos")

# Ver estadísticas
pyhook.print_stats()  # Muestra estadísticas de todos los hooks
pyhook.print_stats("test")  # Estadísticas de un hook específico

# Acceso programático a estadísticas
instance = pyhook.get_global_instance()
stats = instance.get_stats("test")
print(f"Total llamadas: {stats.total_calls}")
```

## 💾 Persistencia

```python
import pyhook
from pyhook.features.persistence import JsonPersistenceBackend

# Configurar persistencia
backend = JsonPersistenceBackend("./hooks.json")
instance = pyhook.get_global_instance()
instance.enable_persistence(backend, auto_save=True, interval=60.0)

# Los hooks se guardan automáticamente
pyhook.use("evento_persistente", lambda x: print(x))

# Guardar manualmente
instance.save_hooks()
```

## 🎭 Ejemplo Completo: Sistema E-commerce

```python
import asyncio
import pyhook
from pyhook import HookPriority

class Order:
    def __init__(self, order_id, user_id, total):
        self.order_id = order_id
        self.user_id = user_id
        self.total = total

@pyhook.hook("order_validation", priority=HookPriority.CRITICAL)
def validate_order(order):
    if order.total <= 0:
        raise ValueError("Total inválido")
    print(f"✓ Orden {order.order_id} validada")

@pyhook.hook("order_processing")
async def process_payment(order):
    print(f"💳 Procesando pago: ${order.total}")
    await asyncio.sleep(0.1)  # Simular API de pago
    print(f"✓ Pago procesado")

@pyhook.hook("order_processing") 
def update_inventory(order):
    print(f"📦 Actualizando inventario para orden {order.order_id}")

@pyhook.conditional_hook(lambda order: order.total > 100)
def vip_processing(order):
    print(f"🌟 Orden VIP: {order.order_id}")

@pyhook.hookable(
    before_hooks=["order_validation"],
    after_hooks=["order_completion"]
)
async def process_order(order):
    print(f"🛍️ Procesando orden {order.order_id}")
    
    # Procesamiento con ejecución paralela
    await pyhook.async_trigger("order_processing", order, 
                              _strategy=ExecutionStrategy.PARALLEL)
    
    return order

# Usar el sistema
async def main():
    order = Order("ORD-001", "user123", 299.99)
    
    processed_order = await process_order(order)
    pyhook.trigger("vip_processing", order)  # Se ejecuta porque total > 100
    
    # Ver estadísticas
    pyhook.print_stats()

asyncio.run(main())
```

## 🧪 Ejecutar Tests de Demostración

El proyecto incluye 10 tests completos que demuestran todas las funcionalidades:

```bash
# Ejecutar test específico
python -m tests.test1  # Hook básico
python -m tests.test2  # Sistema de prioridades  
python -m tests.test3_async  # Hooks asíncronos
python -m tests.test4_validation  # Validación
python -m tests.test5_decorators  # Decoradores
python -m tests.test6_namespaces  # Namespaces
python -m tests.test7_monitoring  # Monitoreo
python -m tests.test8_strategies  # Estrategias de ejecución
python -m tests.test9_persistence  # Persistencia
python -m tests.test10_complete_demo  # Demo completo

# Ejecutar todos los tests
python run_all_tests.py
```

## 📚 API Reference

### Funciones Principales

- `use(name, callback, **options)` - Registrar hook
- `use_once(name, callback, **options)` - Hook de una sola ejecución
- `remove(name, callback=None)` - Eliminar hook(s)
- `trigger(name, *args, **kwargs)` - Disparar hooks síncronos
- `async_trigger(name, *args, **kwargs)` - Disparar hooks asíncronos
- `trigger_with_return(name, *args, **kwargs)` - Obtener valores de retorno
- `list_hooks(name=None)` - Listar hooks registrados
- `clear_hooks(name=None)` - Limpiar hooks

### Decoradores

- `@hook(name, **options)` - Decorador básico de hook
- `@before(hook_name)` - Ejecutar antes de un evento
- `@after(hook_name)` - Ejecutar después de un evento
- `@around(hook_name)` - Ejecutar antes y después
- `@hookable(**options)` - Hacer función "hookeable"
- `@conditional_hook(condition)` - Hook condicional
- `@once_hook(name)` - Hook de una vez
- `@priority_hook(name, priority)` - Hook con prioridad

### Opciones de Configuración

- `priority`: `HookPriority.CRITICAL`, `HIGH`, `NORMAL`, `LOW`, `BACKGROUND`
- `once`: `bool` - Hook de una sola ejecución
- `condition`: `Callable` - Condición para ejecutar
- `filter`: `Callable` - Transformar datos antes de ejecutar
- `validator`: `Callable|dict|type` - Validar datos
- `tags`: `List[str]` - Tags para organización

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**techatlasdev** - [gjimenezdeza@gmail.com](mailto:gjimenezdeza@gmail.com)

- GitHub: [@techatlasdev](https://github.com/techatlasdev)
- Proyecto: [https://github.com/techatlasdev/pyhook](https://github.com/techatlasdev/pyhook)

## 🙏 Reconocimientos

- Inspirado en sistemas de hooks de frameworks modernos
- Construido con tipado estático completo
- Diseñado para alta performance y extensibilidad

---

⭐ **¡Dale una estrella si te gusta PyHook!** ⭐