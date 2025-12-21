module.exports = {
  apps: [
    {
      // ------------------------------------
      // 메인 서버 (Nodejs)
      // ------------------------------------
      name: 'main-server',
      script: 'npm',
      args: 'start',
      cwd: 'apps',
      watch: true,
      ignore_watch: ['node_modules', 'logs'],
      exec_mode: 'cluster',
      instances: 1,
    },
    {
      // ------------------------------------
      // 서브 서버 (FastAPI with .venv)
      // ------------------------------------
      name: 'llm-server',
      
      //윈도우 환경시 '.venv/Scripts/python.exe'으로 변경 필요
      script: '.venv/bin/python',

      args: '-m uvicorn main:app',
      
      cwd: 'LLM',
      
      watch: false,
      exec_mode: 'fork',
    }
  ]
};