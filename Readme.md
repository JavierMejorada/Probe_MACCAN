Seccion A:
1.-  Diferencias entre una notificacion sincrona y otra asincrona:

    Una notiificacion asincrona funciona de manera que el flujo de un programa se ve bloqueado , primeramente el servidor envia la notificacion y espera a que el cliente la reciba antes de continuar con la siguiente instruccion, es la manera mas rapida pero realmente si queremos que algo funcione aunque falle o tarde va a tardar mas de lo esperado.

    Una notificacion asincrona no bloquea el trafico, de forma que el servidor delega el envio de un proceso separado , y ademas continua el resto del codigo sin parar, el cliente puede recibir la notificacio despues a traves de websockets (algo que no sabia hasta hoy ) es mucho mas compleja pero escalable

    Como lo podemos ver, por ejemplo cuando el usuario hace una compra la confirmacion de pafo es asincrona 

2.- Problema del uso de la tabla intermedia , si lo manejamos como una tabla que recibe un booleano como lo habia propuesto en la reunion solo habria un estado de lectura para todos los uduarios, entoces si el usuario A lee la notificacion queda como leida tambien para el usuario B 

    Una tabla intermedia resuelve esto por que crea una  fila por cada par, de la forma -notificacion - usuario permitiendo que cada usuario tenga su propio estado de lectura de forma independiente , mucho mas sencillo 

3.- Que es el Fan Out en las notificaciones:

    El fan out es el proceso de distrubuir una sola notificacion a multiples usuarios , digamos que en base a lo que entendi cuando pasa un evento el sistema abre ese evento para que cada usuario lo reciba.

    ademas tiene el Fan-out on write , al crear la notificacion se generan de inmediato los registros Notificationuser para todos los destinatarios, es rapido de leer pero costoso de dscribir si hay demasiados usuarios

    y por otro lado esta el  fan out on read , solo se guarda la notificacion una vez cuando el usuario entra, se calculan sus notificaciones en ese momento

4.- Cuando usar los websockets

    Polling es cuando el cliente le pregunta al servidor cada cierto tiempo , y tiene razon es mas sencillo perop es ineficiente porq ue genera muchas requests, por otro lado como escuche en la reunion los websockets mantienen esta conezion abierta y bidireccional para que el servidor pueda envair datos al cliente en cualquier momento sin que el cliente pregunte.

    Usariamos los websockets cuandi hay muchos usuarios conectados y el polling generaria muchas requests, las notificaciones deben de llegar en tiempo real como un chat en vivo


    Stack usado:

    Django v4.2
    Django rest framework 
    Celery
    Django channels
    REDIS