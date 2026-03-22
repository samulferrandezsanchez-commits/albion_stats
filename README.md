classDiagram
    %% Jerarquía de Personas
    class Persona {
        +dni
        +nombre
        +apellidos
        +telefono
    }
    class Cliente {
        +edad
        +carnet
        +puntos
        +puede_alquilar()
    }
    class Trabajador {
        <<abstract>>
        +horas
        +sueldo
        +calcular_sueldo()*
    }
    class Jefe
    class Vendedor {
        +numero_alquileres()
    }
    class Limpiador

    Persona <|-- Cliente
    Persona <|-- Trabajador
    Trabajador <|-- Jefe
    Trabajador <|-- Vendedor
    Trabajador <|-- Limpiador

    %% Jerarquía de Vehículos
    class Vehiculo {
        +matricula
        +marca
        +modelo
        +precio_d
        +ocupado
        +echar_gasolina()
    }
    class Coche {
        +num_asientos
    }
    class Furgoneta {
        +capacidad_carga
        +tamaño
        +actualizar_tarifa()
    }
    class Moto {
        +cilindrada
    }

    Vehiculo <|-- Coche
    Vehiculo <|-- Furgoneta
    Vehiculo <|-- Moto

    %% Entidades de negocio
    class Sede {
        +idSede
        +nombre
        +ciudad
    }
    class Reserva {
        +fecha_inicio
        +fecha_fin
        +coinciden_fechas()
    }
    class Alquiler {
        +activo
        +codigo
        +precio_alquiler()
        +iniciar_alquiler()
        +finalizar_alquiler()
    }

    Sede "1" o-- "0..*" Vehiculo : tiene
    Sede "1" o-- "0..*" Trabajador : emplea
    Vehiculo "1" o-- "0..*" Reserva : tiene
    Alquiler --> Cliente : pertenece a
    Alquiler --> Vehiculo : usa
    Alquiler --> Vendedor : gestionado por
