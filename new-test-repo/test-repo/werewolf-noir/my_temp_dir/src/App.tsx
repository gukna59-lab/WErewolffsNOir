/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { Terminal, Download, Bot, Database, Server, Settings, CheckCircle, Cloud } from "lucide-react";

export default function App() {
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-200 p-8 font-sans selection:bg-purple-500/30">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 flex items-start gap-6">
          <div className="p-4 bg-purple-500/10 rounded-xl flex-shrink-0">
            <Bot className="w-12 h-12 text-purple-400" />
          </div>
          <div>
            <h1 className="text-3xl font-semibold text-white tracking-tight mb-2">Telegram-бот "Werewolf Noir"</h1>
            <p className="text-neutral-400 text-lg">Код бота на Python успешно сгенерирован вместе с циклом игры (State Machine).</p>
            <div className="flex flex-wrap items-center gap-2 mt-4">
              <div className="flex items-center gap-2 text-emerald-400 font-medium bg-emerald-400/10 w-fit px-3 py-1.5 rounded-lg border border-emerald-400/20">
                <CheckCircle className="w-5 h-5" />
                Основной каркас и базы данных
              </div>
              <div className="flex items-center gap-2 text-emerald-400 font-medium bg-emerald-400/10 w-fit px-3 py-1.5 rounded-lg border border-emerald-400/20">
                <CheckCircle className="w-5 h-5" />
                Ночные/Дневные фазы и Голосование
              </div>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2 mb-4">
              <Download className="w-5 h-5 text-neutral-400" />
              Скачать код
            </h2>
            <ol className="list-decimal list-inside space-y-3 text-neutral-300">
              <li>Нажмите на <strong>Настройки (шестеренку)</strong>.</li>
              <li>Выберите <span className="text-white hover:underline cursor-pointer">Export to ZIP</span>.</li>
              <li>Откройте папку <code>werewolf_bot</code>.</li>
            </ol>
          </div>

          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
             <h2 className="text-xl font-semibold text-white flex items-center gap-2 mb-4">
              <Cloud className="w-5 h-5 text-neutral-400" />
              Деплой на Render
            </h2>
            <div className="space-y-3 text-neutral-300 text-sm">
                <p>Бот содержит файл <code>render.yaml</code> (Blueprint).</p>
                <ol className="list-decimal list-inside space-y-2">
                    <li>Загрузите код на GitHub.</li>
                    <li>В Render нажмите <b>New &gt; Blueprint</b>.</li>
                    <li>Автоматически разверните воркер <b>Werewolf Noir</b>.</li>
                </ol>
            </div>
          </div>

          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
             <h2 className="text-xl font-semibold text-white flex items-center gap-2 mb-4">
              <Terminal className="w-5 h-5 text-neutral-400" />
              Запуск локально
            </h2>
            <div className="space-y-4">
              <div>
                <p className="text-xs text-neutral-400 mb-1">зависимости:</p>
                <div className="bg-black border border-neutral-800 rounded-lg p-2 font-mono text-xs text-green-400">
                  pip install -r requirements.txt
                </div>
              </div>
              <div>
                <p className="text-xs text-neutral-400 mb-1">запуск:</p>
                <div className="bg-black border border-neutral-800 rounded-lg p-2 font-mono text-xs text-green-400">
                  python main.py
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* File Structure Preview */}
        <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2 mb-6">
              <Database className="w-5 h-5 text-neutral-400" />
              Структура проекта
            </h2>
            <div className="grid gap-3 font-mono text-sm">
                <div className="flex items-center gap-3 p-3 rounded-lg bg-neutral-950/50 border border-neutral-800/50">
                   <Server className="w-4 h-4 text-blue-400"/>
                   <span className="text-white">main.py</span>
                   <span className="text-neutral-500 ml-auto">Точка входа (aiogram Dispatcher)</span>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-neutral-950/50 border border-neutral-800/50">
                   <Settings className="w-4 h-4 text-purple-400"/>
                   <span className="text-white">handlers.py</span>
                   <span className="text-neutral-500 ml-auto">Роутеры, лобби, меню и магазин</span>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-neutral-950/50 border border-neutral-800/50">
                   <Bot className="w-4 h-4 text-orange-400"/>
                   <span className="text-white">game_flow.py</span>
                   <span className="text-neutral-500 ml-auto">Цикл игры (День/Ночь/Таймеры/Гифки)</span>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-neutral-950/50 border border-neutral-800/50">
                   <Database className="w-4 h-4 text-yellow-400"/>
                   <span className="text-white">database.py</span>
                   <span className="text-neutral-500 ml-auto">Схема SQLite (Профили, монеты)</span>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-neutral-950/50 border border-neutral-800/50">
                   <Bot className="w-4 h-4 text-emerald-400"/>
                   <span className="text-white">roles.py</span>
                   <span className="text-neutral-500 ml-auto">Описание каждой роли (Купидон и т.д.)</span>
                </div>
            </div>
          </div>
      </div>
    </div>
  );
}
