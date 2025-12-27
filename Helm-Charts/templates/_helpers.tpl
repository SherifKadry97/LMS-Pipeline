{{/*
Create Docker config JSON for private registry
*/}}
{{- define "library-management-system.dockerconfigjson" -}}
{{- with .Values.secrets.docker }}
{{- $auth := printf "%s:%s" .username .password | b64enc }}
{{- printf "{\"auths\":{\"%s\":{\"username\":\"%s\",\"password\":\"%s\",\"email\":\"%s\",\"auth\":\"%s\"}}}" "index.docker.io" .username .password .email $auth | b64enc }}
{{- end }}
{{- end }}
