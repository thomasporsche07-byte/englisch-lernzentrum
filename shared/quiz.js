/* ===================================================
   shared/quiz.js
   WWM-Quiz-Logik (Wer-wird-Millionär-Stil).
   Globale API:
     window.HRQuiz.init(quizPool, options)
       quizPool: Array<{prompt,options[4],correct,tip,explanation,d:1|2|3}>
       options: {
         finalMessages?: function(pct) -> {msg, emoji}
         phoneFallback?: string  // Fallback-Tipp im Telefonjoker
         resetBtnId?: string     // default: 'quiz-reset'
         containerId?: string    // default: 'quiz-tasks'
         resultId?: string       // default: 'quiz-result'
         progressSelector?: string // default: '#quiz-progress .progress'
       }

   Erfordert globale Helfer:
     window.HRShared.initProgressBar(root, total)
     window.HRShared.shuffle(arr)
   (Werden in scorecards.js definiert.)
   =================================================== */

(function(){
  var ns = window.HRQuiz = window.HRQuiz || {};

  var AMOUNTS = ['50 €','100 €','200 €','300 €','500 €','1.000 €','2.000 €','4.000 €','8.000 €','16.000 €','32.000 €','64.000 €','125.000 €','500.000 €','1.000.000 €'];
  var MILESTONES = [4, 9];

  function defaultFinal(pct){
    if(pct===100) return {msg:'EINE MILLION! 🎉 PERFEKT!', emoji:'🏆'};
    if(pct>=90)   return {msg:'Fast perfekt – das Thema sitzt schon sehr gut!', emoji:'🥇'};
    if(pct>=80)   return {msg:'Richtig stark – die Grundregeln sind klar!', emoji:'🥈'};
    if(pct>=60)   return {msg:'Gut gemacht – noch etwas üben, dann sitzt es!', emoji:'👍'};
    if(pct>=40)   return {msg:'Weiter üben – schau dir die Regelkarten an!', emoji:'💪'};
    return {msg:'Nochmal von vorne – schau dir die Regelkarten an!', emoji:'📚'};
  }

  ns.init = function(quizPool, options){
    options = options || {};
    var finalFn = typeof options.finalMessages === 'function' ? options.finalMessages : defaultFinal;
    var phoneFallback = options.phoneFallback || 'Denk an die Grundregel zu diesem Thema.';
    var resetBtnId = options.resetBtnId || 'quiz-reset';
    var containerId = options.containerId || 'quiz-tasks';
    var resultId = options.resultId || 'quiz-result';
    var progressSel = options.progressSelector || '#quiz-progress .progress';

    var container = document.getElementById(containerId);
    var resultDiv = document.getElementById(resultId);
    var progressRoot = document.querySelector(progressSel);
    if(!container || !resultDiv || !progressRoot){
      console.warn('[HRQuiz] Quiz-DOM nicht gefunden – Quiz wird nicht initialisiert.');
      return;
    }

    var shuffle = (window.HRShared && window.HRShared.shuffle) ? window.HRShared.shuffle : function(a){var b=a.slice();for(var i=b.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=b[i];b[i]=b[j];b[j]=t;}return b;};
    var initProgressBar = (window.HRShared && window.HRShared.initProgressBar) ? window.HRShared.initProgressBar : function(root,total){
      var fill = root.querySelector('.progress-fill');
      var text = root.parentNode.querySelector('.progress-text');
      var _t = total||15;
      return {
        setTotal:function(t){_t=t;},
        update:function(c,d){
          var pct = _t>0 ? Math.round(c/_t*100) : 0;
          if(fill) fill.style.width = pct+'%';
          if(text) text.textContent = 'Fortschritt: '+c+'/'+_t+' richtig ('+pct+'%)';
        },
        resetAnimated:function(){
          if(fill){fill.style.transition='none';fill.style.width='0%';setTimeout(function(){fill.style.transition='';},50);}
          if(text) text.textContent = 'Fortschritt: 0/'+_t+' richtig (0%)';
        }
      };
    };

    var progressCtrl = initProgressBar(progressRoot, 15);
    var questions = [], current = 0, correctCount = 0;
    var phoneUsed = false, audienceUsed = false, fiftyUsed = false;
    var lastHiddenIndices = [];

    function buildLadder(cur){
      var html = '';
      for(var i=AMOUNTS.length-1;i>=0;i--){
        var cls = 'wwm-ladder-row';
        if(MILESTONES.indexOf(i)>=0) cls += ' milestone';
        if(i<cur) cls += ' done';
        if(i===cur) cls += ' current';
        var icon = MILESTONES.indexOf(i)>=0
          ? (i<cur?'✅':i===cur?'🏆':'🛡️')
          : (i<cur?'✓':i===cur?'▶':'');
        html += '<div class="'+cls+'"><span class="wwm-qnum">'+(i+1)+'</span><span class="wwm-amount">'+AMOUNTS[i]+'</span><span style="font-size:11px;margin-left:2px">'+icon+'</span></div>';
      }
      return html;
    }

    function showQuestion(idx){
      if(idx>=questions.length){ showFinal(correctCount, questions.length); return; }
      var q = questions[idx];
      var letters = ['A','B','C','D'];
      var optIndices = [];
      for(var k=0;k<q.options.length;k++) optIndices.push(k);
      for(var i=optIndices.length-1;i>0;i--){
        var j=Math.floor(Math.random()*(i+1));
        var t=optIndices[i]; optIndices[i]=optIndices[j]; optIndices[j]=t;
      }
      var shuffled = optIndices.map(function(i){return q.options[i];});
      var correctShuffled = optIndices.indexOf(q.correct);
      lastHiddenIndices = [];

      var lifelines = [
        {id:'fifty', label:'50/50',         used:fiftyUsed},
        {id:'phone', label:'📞 Joker',      used:phoneUsed},
        {id:'audience', label:'👥 Publikum', used:audienceUsed}
      ];
      var lifelineHtml = lifelines.map(function(l){
        return '<span class="chip'+(l.used?' chip-used':'')+'" data-joker="'+l.id+'">'+l.label+'</span>';
      }).join('');

      var html =
        '<div class="wwm-layout quiz-question-enter">'+
          '<div class="wwm-main">'+
            '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px">'+
              '<div class="wwm-qbadge">Frage '+(idx+1)+' / '+questions.length+' &nbsp;·&nbsp; '+AMOUNTS[idx]+'</div>'+
              '<div class="quiz-streak" id="quiz-streak"></div>'+
            '</div>'+
            '<div class="wwm-lifelines">'+lifelineHtml+'</div>'+
            '<div class="task wwm-stage">'+
              '<div class="prompt">'+q.prompt+'</div>'+
              '<div class="wwm-joker-options" id="wwm-options">'+
                shuffled.map(function(opt,i){
                  return '<button class="wwm-option-btn" data-opt="'+i+'"><span class="wwm-opt-letter">'+letters[i]+'</span><span>'+opt+'</span></button>';
                }).join('')+
              '</div>'+
              '<div id="wwm-joker-extra"></div>'+
              '<div class="feedback" id="wwm-feedback"></div>'+
              '<div id="wwm-explanation" style="display:none" class="quiz-explanation-box"></div>'+
              '<div class="controls" style="margin-top:14px;display:none" id="wwm-next-ctrl">'+
                '<button class="btn green" id="wwm-next">Weiter →</button>'+
              '</div>'+
            '</div>'+
          '</div>'+
          '<div class="wwm-ladder">'+buildLadder(idx)+'</div>'+
        '</div>';
      container.innerHTML = html;
      progressCtrl.update(correctCount, idx);

      var optBtns = container.querySelectorAll('.wwm-option-btn');
      optBtns.forEach(function(btn){
        btn.addEventListener('click', function(){
          var chosen = +btn.dataset.opt;
          optBtns.forEach(function(b){b.disabled=true;});
          var fb = document.getElementById('wwm-feedback');
          var expl = document.getElementById('wwm-explanation');
          var nctrl = document.getElementById('wwm-next-ctrl');
          if(chosen === correctShuffled){
            btn.style.background='linear-gradient(90deg,rgba(0,180,80,.3),rgba(0,150,60,.2))';
            btn.style.borderColor='#00e676';
            fb.textContent='✓ Richtig! +'+AMOUNTS[idx];
            fb.className='feedback ok';
            correctCount++;
            progressCtrl.update(correctCount, idx+1);
          } else {
            btn.style.background='linear-gradient(90deg,rgba(180,0,0,.3),rgba(140,0,0,.2))';
            btn.style.borderColor='#ff5555';
            var correctBtn = container.querySelectorAll('.wwm-option-btn')[correctShuffled];
            if(correctBtn){
              correctBtn.style.background='linear-gradient(90deg,rgba(0,180,80,.3),rgba(0,150,60,.2))';
              correctBtn.style.borderColor='#00e676';
            }
            fb.innerHTML='✗ Falsch! Richtige Antwort: <b>'+shuffled[correctShuffled]+'</b>';
            fb.className='feedback bad';
            if(q.explanation){ expl.innerHTML=q.explanation; expl.style.display='block'; }
            if(q.tip){
              var tb = document.createElement('div');
              tb.className='quiz-tip-box';
              tb.innerHTML='💡 <b>Tipp:</b> '+q.tip;
              nctrl.parentNode.insertBefore(tb, nctrl);
            }
            nctrl.style.display='flex';
            var nextBtn = document.getElementById('wwm-next');
            if(nextBtn){
              nextBtn.textContent='Ergebnis ansehen →';
              nextBtn.className='btn gray';
              nextBtn.dataset.next='1';
              nextBtn.addEventListener('click', function(){ showFinal(correctCount, questions.length); });
            }
            return;
          }
          if(q.explanation){ expl.innerHTML=q.explanation; expl.style.display='block'; }
          nctrl.style.display='flex';
          var nextBtn = document.getElementById('wwm-next');
          if(nextBtn){
            nextBtn.addEventListener('click', function(){
              current++;
              showQuestion(current);
              setTimeout(function(){
                if(typeof TTS!=='undefined' && TTS.injectAll) TTS.injectAll();
              }, 60);
            });
          }
        });
      });

      container.querySelectorAll('.chip[data-joker]').forEach(function(chip){
        chip.addEventListener('click', function(){
          var joker = chip.dataset.joker;
          if(chip.classList.contains('chip-used')) return;
          chip.classList.add('chip-used');
          if(joker==='fifty'){
            fiftyUsed = true;
            var wrong = [];
            container.querySelectorAll('.wwm-option-btn').forEach(function(b,i){if(i!==correctShuffled)wrong.push(i);});
            var hide = wrong.sort(function(){return Math.random()-0.5;}).slice(0,2);
            lastHiddenIndices = hide;
            hide.forEach(function(i){
              var b = container.querySelectorAll('.wwm-option-btn')[i];
              if(b){ b.style.opacity='0.2'; b.disabled=true; }
            });
          } else if(joker==='phone'){
            phoneUsed = true;
            var ruleHint = q.tip || phoneFallback;
            var extra = document.getElementById('wwm-joker-extra');
            extra.innerHTML='<div class="wwm-phone-bubble"><div class="wwm-phone-icon">📞</div><div class="wwm-phone-text"><b>Dein Lehrer meldet sich:</b><br>'+ruleHint+'</div></div>';
          } else if(joker==='audience'){
            audienceUsed = true;
            var pcts = [];
            for(var ii=0; ii<4; ii++){
              var v = ii===correctShuffled
                ? Math.floor(40 + Math.random()*35)
                : Math.floor(5  + Math.random()*20);
              pcts.push(v);
            }
            var sum = pcts.reduce(function(a,b){return a+b;}, 0);
            var scale = 100/sum;
            var scaled = pcts.map(function(v){return Math.round(v*scale);});
            var colors = ['#4fc3f7','#ef5350','#66bb6a','#ffb74d'];
            var extra2 = document.getElementById('wwm-joker-extra');
            var barsHtml = shuffled.map(function(opt,i){
              return '<div class="wwm-audience-col">'+
                '<div class="wwm-audience-pct">'+scaled[i]+'%</div>'+
                '<div class="wwm-audience-bar" style="height:'+Math.max(4, Math.round(scaled[i]*0.8))+'px;background:'+colors[i]+';align-self:flex-end"></div>'+
                '<div class="wwm-audience-label">'+letters[i]+'</div>'+
              '</div>';
            }).join('');
            extra2.innerHTML='<div class="wwm-audience-box"><div class="wwm-audience-title">👥 Publikumsjoker</div><div class="wwm-audience-bars">'+barsHtml+'</div></div>';
          }
        });
      });

      setTimeout(function(){
        if(typeof TTS!=='undefined' && TTS.injectAll) TTS.injectAll();
      }, 60);
    }

    function showFinal(correct, total){
      var pct = Math.round(correct/total*100);
      var f = finalFn(pct) || defaultFinal(pct);
      container.innerHTML='';
      resultDiv.style.display='block';
      resultDiv.innerHTML =
        '<div style="padding:28px 22px;text-align:center">'+
          '<div style="font-size:52px;margin-bottom:8px">'+f.emoji+'</div>'+
          '<div style="font-size:26px;font-weight:900;color:#ffcc00;margin-bottom:8px" class="score">'+correct+' / '+total+'</div>'+
          '<div style="font-size:17px;font-weight:700;color:#fff;margin-bottom:16px">'+f.msg+'</div>'+
          '<button class="btn" style="background:linear-gradient(135deg,#0d3080,#1e4db5);color:#ffecb3;border:1px solid rgba(255,204,0,.4);padding:12px 28px;font-size:15px" onclick="document.getElementById(\''+resetBtnId+'\').click()">🔄 Nochmal spielen</button>'+
        '</div>';
      progressCtrl.update(correct, total);
    }

    function startGame(){
      current = 0; correctCount = 0;
      phoneUsed = false; audienceUsed = false; fiftyUsed = false;
      lastHiddenIndices = [];
      resultDiv.style.display='none';
      var byDiff = function(d){return quizPool.filter(function(q){return q.d===d;});};
      var d1 = shuffle(byDiff(1)).slice(0,4);
      var d2 = shuffle(byDiff(2)).slice(0,5);
      var d3 = shuffle(byDiff(3)).slice(0,6);
      questions = d1.concat(d2).concat(d3);
      progressCtrl.setTotal(questions.length);
      progressCtrl.update(0,0);
      showQuestion(0);
    }

    var resetBtn = document.getElementById(resetBtnId);
    if(resetBtn) resetBtn.addEventListener('click', startGame);

    // Erst beim ersten Öffnen des Akkordeons starten
    var quizDetails = document.getElementById('wwm-quiz');
    if(quizDetails && quizDetails.tagName === 'DETAILS'){
      var started = false;
      quizDetails.addEventListener('toggle', function(){
        if(quizDetails.open && !started){
          started = true;
          startGame();
        }
      });
      // Falls Akkordeon bereits offen (z.B. wegen reopen), direkt starten
      if(quizDetails.open){
        started = true;
        startGame();
      }
    } else {
      // Kein Akkordeon-Wrapper → direkt starten
      startGame();
    }
  };
})();
