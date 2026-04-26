/* ===================================================
   shared/tutor.js
   KI-Tutor (Gemini Flash über eigenen Worker-Endpunkt).
   Liest beim Laden window.TUTOR_CONFIG, baut den
   System-Prompt aus shared/tutor_base_prompt.txt +
   Topic-spezifischen Daten zusammen, injiziert das
   Akkordeon-Markup in einen Mount-Point und wired
   alle Events.

   TUTOR_CONFIG-Schema:
     {
       topic:           string,    // z.B. "to be (am/is/are)"
       grade:           number,    // 5..10
       unit:            number,    // Lighthouse-Unit
       rules:           string[],  // Kurzform der Regelpunkte (für Badges)
       welcomeMessage:  string,    // HTML-erlaubt
       quickChips:      string[],  // Beispielfragen
       typicalErrors?:  string[],  // typische Schülerfehler (für System-Prompt)
       mountId?:        string,    // Default: 'tutor-mount'
       endpoint?:       string,    // Default: bekannter Worker-URL
       basePromptUrl?:  string     // Default: '../shared/tutor_base_prompt.txt'
     }

   API:
     window.kiSend(text?)
     window.kiClear()
   =================================================== */

(function(){
  var DEFAULT_ENDPOINT = 'https://gemini-direct.thomasporsche07.workers.dev/';
  var DEFAULT_BASE_PROMPT_URL = '../shared/tutor_base_prompt.txt';

  // Fallback-Base-Prompt (wenn fetch fehlschlägt, z.B. bei file:// Aufruf)
  var FALLBACK_BASE_PROMPT =
    'Du bist ein Englisch-Tutor für deutsche Realschüler.\n\n' +
    'DEINE AUFGABE:\n' +
    '- Du hilfst beim Verständnis englischer Grammatik zum gewählten Thema.\n' +
    '- Du erklärst Regeln auf Deutsch, sehr einfach.\n' +
    '- Du gibst NICHT die fertige Lösung – nur Hinweise.\n\n' +
    'REGELN:\n' +
    '1. Antworte IMMER auf Deutsch.\n' +
    '2. Antworte KURZ: maximal 4 Sätze.\n' +
    '3. Vermeide Fachbegriffe, die ein 12-Jähriger nicht kennt.\n' +
    '4. Sei ermutigend und geduldig.';

  function escapeHtml(s){
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function buildAccordionHtml(cfg){
    var topicSafe = escapeHtml(cfg.topic || 'das Thema');
    var welcome = cfg.welcomeMessage || (
      '<strong>👋 Hallo! Ich bin dein KI-Tutor.</strong><br>' +
      'Ich helfe dir, das Thema „' + topicSafe + '" besser zu verstehen. ' +
      'Stell mir Fragen, bitte um Beispiele oder schick mir einen Satz zum Prüfen. ' +
      'Ich gebe dir Tipps – aber keine fertigen Lösungen!'
    );
    var badgesHtml = (cfg.rules || []).map(function(r){
      return '<span class="ki-badge">' + escapeHtml(r) + '</span>';
    }).join('');
    var chipsHtml = (cfg.quickChips || []).map(function(c){
      var safe = String(c).replace(/"/g, '&quot;');
      return '<button class="ki-chip" onclick="kiSend(this.textContent)">' + escapeHtml(c) + '</button>';
    }).join('');

    return '' +
      '<div class="quiz-divider"><span>🤖 KI-Tutor</span></div>' +
      '<details class="accordion" id="acc-ki">' +
        '<summary><span class="acc-num">🤖</span>KI-Tutor – Frag mich alles zu „' + topicSafe + '"</summary>' +
        '<div class="content">' +
          '<div class="ki-wrap">' +
            '<div class="ki-welcome">' + welcome +
              (badgesHtml ? '<div class="ki-badges">' + badgesHtml + '</div>' : '') +
            '</div>' +
            (chipsHtml ? '<div class="ki-chips">' + chipsHtml + '</div>' : '') +
            '<div class="ki-messages" id="ki-messages"></div>' +
            '<div class="ki-err" id="ki-err" style="display:none"></div>' +
            '<div class="ki-input-row">' +
              '<button class="ki-clear" id="ki-clear-btn" title="Gespräch löschen" onclick="kiClear()" disabled>🗑</button>' +
              '<input class="ki-input" id="ki-input" type="text" placeholder="Deine Frage zum Thema …" maxlength="300" />' +
              '<button class="ki-send" id="ki-send-btn" onclick="kiSend()" title="Senden">➤</button>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</details>';
  }

  function buildSystemPrompt(basePrompt, cfg){
    var lines = [basePrompt.trim(), ''];
    lines.push('THEMA DIESER SEITE:');
    lines.push('- Topic: ' + (cfg.topic || '(unbekannt)'));
    if(cfg.grade) lines.push('- Klassenstufe: Klasse ' + cfg.grade);
    if(cfg.unit)  lines.push('- Lighthouse-Unit: Unit ' + cfg.unit);
    if(Array.isArray(cfg.rules) && cfg.rules.length){
      lines.push('');
      lines.push('REGELPUNKTE, an denen du dich orientieren kannst:');
      cfg.rules.forEach(function(r){ lines.push('- ' + r); });
    }
    if(Array.isArray(cfg.typicalErrors) && cfg.typicalErrors.length){
      lines.push('');
      lines.push('TYPISCHE FEHLER, die Schüler bei diesem Thema machen:');
      cfg.typicalErrors.forEach(function(e){ lines.push('- ' + e); });
    }
    lines.push('');
    lines.push('Wenn der Schüler über etwas anderes als „' + (cfg.topic || 'dieses Thema') + '" fragt, lenke freundlich zurück.');
    return lines.join('\n');
  }

  function loadBasePrompt(url){
    return fetch(url, {cache:'no-cache'})
      .then(function(r){ if(!r.ok) throw new Error('HTTP '+r.status); return r.text(); })
      .catch(function(){ return FALLBACK_BASE_PROMPT; });
  }

  function init(){
    var cfg = window.TUTOR_CONFIG;
    if(!cfg){
      console.warn('[Tutor] window.TUTOR_CONFIG fehlt – Tutor wird nicht initialisiert.');
      return;
    }
    var mountId = cfg.mountId || 'tutor-mount';
    var mount = document.getElementById(mountId);
    if(!mount){
      console.warn('[Tutor] Mount-Point #' + mountId + ' fehlt – Tutor wird nicht initialisiert.');
      return;
    }
    mount.innerHTML = buildAccordionHtml(cfg);

    var endpoint = cfg.endpoint || DEFAULT_ENDPOINT;
    var basePromptUrl = cfg.basePromptUrl || DEFAULT_BASE_PROMPT_URL;

    var systemPrompt = '';
    var kiHistory = [];

    loadBasePrompt(basePromptUrl).then(function(base){
      systemPrompt = buildSystemPrompt(base, cfg);
    });

    function kiClear(){
      kiHistory = [];
      var c = document.getElementById('ki-messages');
      if(c) c.innerHTML = '';
      var errEl = document.getElementById('ki-err');
      if(errEl) errEl.style.display = 'none';
      var clearBtn = document.getElementById('ki-clear-btn');
      if(clearBtn) clearBtn.disabled = true;
      var inputEl = document.getElementById('ki-input');
      if(inputEl) inputEl.focus();
    }

    function kiXHR(payload){
      payload.generationConfig = Object.assign({maxOutputTokens:400}, payload.generationConfig||{});
      return fetch(endpoint, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(payload)
      }).then(function(r){
        if(!r.ok){
          return r.json().then(function(e){
            throw new Error((e.error&&e.error.message) || 'HTTP '+r.status);
          }).catch(function(){
            throw new Error('HTTP '+r.status);
          });
        }
        return r.json();
      }).then(function(data){
        var text = (data.candidates && data.candidates[0] && data.candidates[0].content
          && data.candidates[0].content.parts && data.candidates[0].content.parts[0]
          && data.candidates[0].content.parts[0].text) || '';
        return text.trim();
      });
    }

    function kiAppendMsg(role, text){
      var c = document.getElementById('ki-messages');
      var d = document.createElement('div');
      d.className = 'ki-msg ' + role;
      var av = document.createElement('div');
      av.className = 'ki-avatar';
      av.textContent = role === 'user' ? 'Du' : '🤖';
      var bu = document.createElement('div');
      bu.className = 'ki-bubble';
      bu.innerHTML = String(text)
        .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
        .replace(/\n/g,'<br>');
      d.appendChild(av);
      d.appendChild(bu);
      c.appendChild(d);
      d.scrollIntoView({behavior:'smooth', block:'nearest'});
      return d;
    }

    function kiAppendTyping(){
      var c = document.getElementById('ki-messages');
      var d = document.createElement('div');
      d.className = 'ki-msg ai';
      d.id = 'ki-typing';
      d.innerHTML = '<div class="ki-avatar">🤖</div><div class="ki-bubble"><div class="ki-typing"><span></span><span></span><span></span></div></div>';
      c.appendChild(d);
      d.scrollIntoView({behavior:'smooth', block:'nearest'});
      return d;
    }

    function kiSend(quickText){
      var inputEl = document.getElementById('ki-input');
      var sendBtn = document.getElementById('ki-send-btn');
      var clearBtn = document.getElementById('ki-clear-btn');
      var errEl = document.getElementById('ki-err');
      var text = quickText || (inputEl ? inputEl.value.trim() : '');
      if(!text) return;
      if(inputEl) inputEl.value = '';
      if(errEl) errEl.style.display = 'none';
      if(sendBtn) sendBtn.disabled = true;
      kiAppendMsg('user', text);
      var typing = kiAppendTyping();

      var contents = [];
      contents.push({role:'user',  parts:[{text: systemPrompt || FALLBACK_BASE_PROMPT}]});
      contents.push({role:'model', parts:[{text:'Verstanden! Ich helfe dir bei diesem Thema.'}]});
      for(var i=0; i<kiHistory.length; i++){ contents.push(kiHistory[i]); }
      contents.push({role:'user', parts:[{text: text}]});

      kiXHR({
        contents: contents,
        generationConfig: {temperature:0.7, maxOutputTokens:300, thinkingConfig:{thinkingBudget:0}}
      }).then(function(reply){
        kiHistory.push({role:'user',  parts:[{text: text}]});
        kiHistory.push({role:'model', parts:[{text: reply}]});
        if(kiHistory.length > 20) kiHistory = kiHistory.slice(kiHistory.length - 20);
        if(typing && typing.parentNode) typing.parentNode.removeChild(typing);
        kiAppendMsg('ai', reply);
        if(clearBtn) clearBtn.disabled = false;
      }).catch(function(e){
        if(typing && typing.parentNode) typing.parentNode.removeChild(typing);
        if(errEl){
          errEl.textContent = '⚠️ Fehler: ' + e.message;
          errEl.style.display = 'block';
        }
      }).then(function(){
        if(sendBtn) sendBtn.disabled = false;
        if(inputEl) inputEl.focus();
      });
    }

    // Eingabezeile: Enter sendet
    var inputEl = document.getElementById('ki-input');
    if(inputEl){
      inputEl.addEventListener('keydown', function(e){
        if(e.key === 'Enter' && !e.shiftKey){
          e.preventDefault();
          kiSend();
        }
      });
    }

    // Globale Funktionen für Inline-Handler / Quick-Chips
    window.kiSend = kiSend;
    window.kiClear = kiClear;
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
