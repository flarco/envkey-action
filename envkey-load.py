import os, envkey

secrets = envkey.fetch_env(os.getenv('ENVKEY'), cache_enabled=False)

multiline_template = '''
echo '{k}<<EEEE123123OOOO987987FFFFF
{v}
EEEE123123OOOO987987FFFFF' >> "$GITHUB_ENV"
'''

bash_lines = ['#!/usr/bin/env bash', '']
mask_lines = ['#!/usr/bin/bash', '']
env_lines = []
env_sh_lines = []
for k, val in secrets.items():
  v = val.replace("'", """'"'"'""") # escape single quote

  # so the value is masked
  if '\n' in val:
    bash_lines.append(multiline_template.replace('{k}', k).replace('{v}', v))
    for l in v.splitlines():
      mask_lines.append(f"""echo '::add-mask::{l.strip()}'""")
  else:
    bash_lines.append(f"""echo '{k}={v}' >> $GITHUB_ENV""")
    mask_lines.append(f"""echo '::add-mask::{v.strip()}'""")
    env_lines.append(f"""{k}='{v}'""")
    env_sh_lines.append(f"""export '{k}'='{v}'""")
  

# replace re-used env vars
for k, val in secrets.items():
  key = '${' + k + '}'
  for i, _ in enumerate(bash_lines):
    bash_lines[i] = bash_lines[i].replace(key, val)
  for i, _ in enumerate(env_lines):
    env_lines[i] = env_lines[i].replace(key, val)

print('writing secrets.sh', flush=True)
with open('/tmp/secrets.sh', 'w') as file:
  file.write('\n'.join(bash_lines))

with open('/tmp/masks.sh', 'w') as file:
  file.write('\n'.join(mask_lines))

if os.getenv('DOTENV') == 'true':
  print('writing .env', flush=True)
  with open('.env', 'w') as file:
    file.write('\n'.join(env_lines))

if os.getenv('DOTENV_SH') == 'true':
  print('writing .env.sh', flush=True)
  with open('.env.sh', 'w') as file:
    file.write('\n'.join(env_sh_lines))
