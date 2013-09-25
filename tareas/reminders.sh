#!/bin/bash
PATH="/bin:/sbin/:/usr/bin:/usr/sbin"
workdir="/home/zoe/gul-zoe/"
pushd "$workdir/tareas" &>/dev/null

dayOfTheWeek="$(date +%u)"
month="$(date +%m)"
day="$(date +%d)"
basenameReunionMensual="reunion_mensual_reminder"
basenameHolaMundo="holamundo_reminder"
basenameJuernes="juernesontour"

#
# Recordatorio reunion mensual
#
if [ "$dayOfTheWeek" -eq 1 ] && [ "$day" -le 10 ] && [ "$day" -ge 4 ];then #Segundo lunes de mes
  listaDeCorreos=($(echo ${workdir}/lib/messages/${basenameReunionMensual}*))
  seleccionado=$((RANDOM % ${#listaDeCorreos[*]}))
  cat ${listaDeCorreos[$seleccionado]} | ./sendmail.sh "[ORG] Reunión este viernes" "gul@gul.uc3m.es"
fi

#
# Recordatorio HolaMundo
#
if [ "$dayOfTheWeek" -eq 1 ] && [ "$day" -le 17 ] && [ "$day" -ge 11 ];then #Tercer lunes de mes
  basename=$basenameHolaMundo
  listaDeCorreos=($(echo ${workdir}/lib/messages/${basename}*))
  seleccionado=$((RANDOM % ${#listaDeCorreos[*]}))
  cat ${listaDeCorreos[$seleccionado]} | ./sendmail.sh "Este viernes toca HolaMundo" "radio@gul.uc3m.es"
fi

#
# Recordatorio JuernesOnTour
#
if [ "$dayOfTheWeek" -eq 1 ] && [ "$day" -le 17 ] && [ "$day" -ge 11 ];then #Tercer lunes de mes
  basename=$basenameJuernes
  listaDeCorreos=($(echo ${workdir}/lib/messages/${basename}*))
  seleccionado=$((RANDOM % ${#listaDeCorreos[*]}))
  cat ${listaDeCorreos[$seleccionado]} | ./sendmail.sh "Este jueves te espero en JuernesOnTour" "nairdcr@gmail.com"
fi

