/* ===================================================
   shared/scorecards.js
   Gemeinsame Helfer:
     - Score-Karten (checkCelebration, showResultBanner)
     - „Alle prüfen"-Auswertung (computeAllCheckResult)
     - Reset-Hooks (clearBanners, resetAllSections)
     - Dark-Mode-Toggle (initDarkMode)
     - TTS-Modul (TTS-Objekt + Toggle-Setup)
     - Custom-Confirm (customConfirm)
     - Reset-All-Button-Setup (initResetAllButton)
     - Kleine Utilities: shuffle, initProgressBar
   Globale API:
     window.HRShared.shuffle(arr)
     window.HRShared.initProgressBar(root, total)
     window.HRShared.checkCelebration(container, message?)
     window.HRShared.showResultBanner(container, ok, total, opts?)
     window.HRShared.clearBanners(container)
     window.HRShared.initDarkMode(btnId, lsKey)
     window.HRShared.initTTS(btnId)         → setzt window.TTS
     window.HRShared.customConfirm(msg, onOk, onCancel?)  // braucht #confirm-modal im DOM
     window.HRShared.initResetAllButton(btnId, sectionResetIds, lsKeys)
   =================================================== */

(function(){
  var ns = window.HRShared = window.HRShared || {};

  // ===== Utility: Shuffle (Fisher-Yates) =====
  ns.shuffle = function(arr){
    var b = arr.slice();
    for(var i=b.length-1;i>0;i--){
      var j = Math.floor(Math.random()*(i+1));
      var t = b[i]; b[i] = b[j]; b[j] = t;
    }
    return b;
  };

  // ===== ProgressBar-Controller =====
  ns.initProgressBar = function(root, total){
    var _total = total || 15;
    var fill = root ? root.querySelector('.progress-fill') : null;
    var textEl = root ? root.parentElement.querySelector('.progress-text') : null;
    var summaryEl = root ? root.closest('details') : null;
    var titleEl = summaryEl ? summaryEl.querySelector('summary') : null;
    return {
      setTotal:function(t){ _total = t; },
      update:function(correct, done){
        var pct = _total > 0 ? Math.round(correct/_total*100) : 0;
        if(fill) fill.style.width = pct + '%';
        if(textEl) textEl.textContent = 'Fortschritt: ' + correct + '/' + _total + ' richtig (' + pct + '%)';
        if(titleEl){
          var base = titleEl.dataset.titleBase || (titleEl.dataset.titleBase = titleEl.textContent.replace(' ✓','').trim());
          if(correct === _total && _total > 0){ titleEl.textContent = base + ' ✓'; }
          else { titleEl.textContent = base; }
        }
      },
      resetAnimated:function(){
        if(fill){
          fill.style.transition = 'none';
          fill.style.width = '0%';
          setTimeout(function(){ fill.style.transition = ''; }, 50);
        }
        if(textEl) textEl.textContent = 'Fortschritt: 0/' + _total + ' richtig (0%)';
        if(titleEl && titleEl.dataset.titleBase) titleEl.textContent = titleEl.dataset.titleBase;
      }
    };
  };

  // ===== Score: Celebrate-Banner =====
  ns.checkCelebration = function(container, message){
    var allTasks = container.querySelectorAll('.task');
    if(!allTasks.length) return;
    var solved = 0;
    allTasks.forEach(function(t){
      if(t.classList.contains('task--solved')) solved++;
    });
    if(solved !== allTasks.length) return;
    if(container.querySelector('.celebrate-banner')) return;
    var banner = document.createElement('div');
    banner.className = 'celebrate-banner';
    banner.innerHTML = message || '🎉 Perfekt! Alle Aufgaben richtig – super gemacht!';
    container.insertBefore(banner, container.firstChild);
    setTimeout(function(){
      banner.scrollIntoView({behavior:'smooth', block:'nearest'});
    }, 80);
  };

  // ===== Score: Result-Banner + Error-List nach „Alle prüfen" =====
  ns.showResultBanner = function(container, ok, total, opts){
    opts = opts || {};
    ns.clearBanners(container);
    var pct = total > 0 ? Math.round(ok/total*100) : 0;
    var cls = pct === 100 ? 'result-green' : pct >= 70 ? 'result-orange' : 'result-red';
    var emoji = pct === 100 ? '✅' : pct >= 70 ? '🟡' : '🔴';
    var headline = pct === 100 ? 'Alle gelöst!' : pct >= 70 ? 'Guter Fortschritt' : 'Noch üben';
    var banner = document.createElement('div');
    banner.className = 'result-banner ' + cls;
    banner.innerHTML = emoji + ' ' + headline + ' – ' + ok + '/' + total + ' richtig (' + pct + '%)';
    container.insertBefore(banner, container.firstChild);

    if(Array.isArray(opts.wrongItems) && opts.wrongItems.length){
      var el = document.createElement('div');
      el.className = 'error-list';
      var html = '<div style="font-weight:800;color:#b91c1c;margin-bottom:6px;">✗ Noch nicht richtig (' + opts.wrongItems.length + '):</div>';
      html += opts.wrongItems.map(function(w){
        var prompt = (w.prompt || '').replace(/<[^>]+>/g, '');
        if(prompt.length > 80) prompt = prompt.substring(0, 80) + '…';
        return '<div style="padding:3px 0;border-top:1px solid #fee2e2;">' + prompt + '</div>';
      }).join('');
      el.innerHTML = html;
      container.insertBefore(el, banner.nextSibling);
    }
    setTimeout(function(){
      banner.scrollIntoView({behavior:'smooth', block:'nearest'});
    }, 80);
  };

  // ===== Reset: alle Banner aus einem Container entfernen =====
  ns.clearBanners = function(container){
    container.querySelectorAll('.result-banner, .celebrate-banner, .error-list').forEach(function(el){
      el.remove();
    });
    container.querySelectorAll('.task--wrong').forEach(function(t){
      t.classList.remove('task--wrong');
    });
  };

  // ===== Dark-Mode-Toggle =====
  ns.initDarkMode = function(btnId, lsKey){
    var btn = document.getElementById(btnId || 'dark-toggle');
    if(!btn) return;
    var key = lsKey || 'darkMode';
    var saved = false;
    try{ saved = localStorage.getItem(key) === '1'; }catch(e){}
    if(saved){
      document.body.classList.add('dark-mode');
      btn.textContent = '☀️ Hell';
    }
    btn.addEventListener('click', function(){
      var isDark = document.body.classList.toggle('dark-mode');
      btn.textContent = isDark ? '☀️ Hell' : '🌙 Dark Mode';
      try{ localStorage.setItem(key, isDark ? '1' : '0'); }catch(e){}
    });
  };

  // ===== TTS-Modul =====
  ns.initTTS = function(btnId){
    var TTS = {
      enabled: false,
      synth: window.speechSynthesis || null,
      current: null,
      voices: [],
      getLang: function(lang){
        if(!this.synth) return null;
        if(!this.voices.length) this.voices = this.synth.getVoices();
        var v = this.voices.find(function(v){return v.lang===lang && v.localService;});
        if(!v) v = this.voices.find(function(v){return v.lang===lang;});
        if(!v) v = this.voices.find(function(v){return v.lang.indexOf(lang.split('-')[0])===0;});
        return v || null;
      },
      speak: function(text, lang){
        if(!this.synth) return;
        try{ this.synth.cancel(); }catch(e){}
        var u = new SpeechSynthesisUtterance(text.replace(/<[^>]+>/g, ''));
        u.lang = lang || 'en-GB';
        u.rate = 0.9;
        u.pitch = 1;
        var v = this.getLang(lang || 'en-GB');
        if(v) u.voice = v;
        this.current = u;
        try{ this.synth.speak(u); }catch(e){}
      },
      createBtn: function(text, lang, extraStyle){
        var btn = document.createElement('button');
        btn.className = 'tts-btn tts-flag-btn';
        btn.title = 'Vorlesen (' + (lang === 'de-DE' ? 'Deutsch' : 'Englisch') + ')';
        btn.textContent = lang === 'de-DE' ? '🇩🇪' : '🇬🇧';
        if(extraStyle) btn.style.cssText = extraStyle;
        var self = this;
        btn.addEventListener('click', function(e){
          e.stopPropagation();
          if(!self.enabled) return;
          self.speak(text, lang);
        });
        return btn;
      },
      injectAll: function(){
        if(!this.enabled) return;
        var processed = new WeakSet();
        var self = this;
        document.querySelectorAll('.task .prompt, .solution, .quiz-explanation-box, .wwm-stage .prompt').forEach(function(el){
          if(processed.has(el)) return;
          processed.add(el);
          var raw = el.getAttribute('data-tts-text') || el.textContent.replace(/<[^>]+>/g, ' ').trim();
          if(!raw) return;
          if(!el.querySelector('.tts-flag-btn')){
            var de = self.createBtn(raw, 'de-DE');
            var en = self.createBtn(raw, 'en-GB');
            el.appendChild(de);
            el.appendChild(en);
          }
        });
      }
    };

    if(TTS.synth && TTS.synth.onvoiceschanged !== undefined){
      TTS.synth.onvoiceschanged = function(){ TTS.voices = TTS.synth.getVoices(); };
    }
    setTimeout(function(){ if(TTS.synth) TTS.voices = TTS.synth.getVoices(); }, 300);

    window.TTS = TTS; // global verfügbar (für Quiz, etc.)

    var btn = document.getElementById(btnId || 'tts-toggle');
    if(btn){
      btn.addEventListener('click', function(){
        TTS.enabled = !TTS.enabled;
        if(TTS.enabled){
          btn.classList.add('tts-on');
          btn.textContent = '🔊 Vorlesen ✓';
          setTimeout(function(){ TTS.injectAll(); }, 60);
        } else {
          btn.classList.remove('tts-on');
          btn.textContent = '🔊 Vorlesen';
          if(TTS.synth) try{ TTS.synth.cancel(); }catch(e){}
          document.querySelectorAll('.tts-btn').forEach(function(b){ b.remove(); });
        }
      });
    }
    return TTS;
  };

  // ===== Custom-Confirm-Modal =====
  // Erfordert ein DOM-Element wie:
  //   <div id="confirm-modal" style="display:none" class="confirm-overlay">
  //     <div class="confirm-box">
  //       <p id="confirm-msg">…</p>
  //       <div class="confirm-btns">
  //         <button class="btn primary" id="confirm-ok">Ja</button>
  //         <button class="btn ghost"   id="confirm-cancel">Abbrechen</button>
  //       </div>
  //     </div>
  //   </div>
  // Falls nicht vorhanden, fällt es auf window.confirm() zurück.
  ns.customConfirm = function(msg, onOk, onCancel){
    var modal = document.getElementById('confirm-modal');
    if(!modal){
      if(window.confirm(msg)){ onOk && onOk(); }
      else { onCancel && onCancel(); }
      return;
    }
    var msgEl = document.getElementById('confirm-msg');
    var okBtn = document.getElementById('confirm-ok');
    var cancelBtn = document.getElementById('confirm-cancel');
    if(msgEl) msgEl.textContent = msg;
    modal.style.display = 'flex';
    function close(){
      modal.style.display = 'none';
      if(okBtn) okBtn.onclick = null;
      if(cancelBtn) cancelBtn.onclick = null;
    }
    if(okBtn) okBtn.onclick = function(){ close(); onOk && onOk(); };
    if(cancelBtn) cancelBtn.onclick = function(){ close(); onCancel && onCancel(); };
  };
  // Auch global (für Inline-onclick-Handler):
  window.customConfirm = ns.customConfirm;

  // ===== Reset-All-Button =====
  // sectionResetIds: Array<string>  – IDs der pro-Sektion-Reset-Buttons (werden geklickt)
  // lsKeys:          Array<string>  – LocalStorage-Keys, die gelöscht werden sollen
  ns.initResetAllButton = function(btnId, sectionResetIds, lsKeys){
    var btn = document.getElementById(btnId || 'reset-all-btn');
    if(!btn) return;
    btn.addEventListener('click', function(){
      ns.customConfirm('Gesamten Fortschritt zurücksetzen?', function(){
        // 1. LocalStorage-Keys löschen
        (lsKeys || []).forEach(function(key){
          try{ localStorage.removeItem(key); }catch(e){}
        });
        // 2. Pro-Sektion-Reset-Buttons klicken,
        //    aber dabei customConfirm umgehen, sonst kommt jeder Bestätigungsdialog einzeln.
        var origConfirm = window.customConfirm;
        window.customConfirm = function(m, cb){ cb && cb(); };
        try{
          (sectionResetIds || []).forEach(function(id){
            var b = document.getElementById(id);
            if(b) b.click();
          });
        } finally {
          window.customConfirm = origConfirm;
        }
      });
    });
  };
})();
