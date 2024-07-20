       function updateLineNumbers() {
            const editor = document.getElementById('code-editor');
            const lineNumbers = document.getElementById('line-numbers');
            const lines = editor.value.split('\n').length;
            lineNumbers.innerHTML = Array(lines).fill(0).map((_, i) => `<div>${i + 1}</div>`).join('');
        }

        function syncScroll() {
            const editor = document.getElementById('code-editor');
            const lineNumbers = document.getElementById('line-numbers');
            lineNumbers.scrollTop = editor.scrollTop;
        }
       document.getElementById('minimize-btn').addEventListener('click', function () {
            var editorSection = document.getElementById('editor-section');
            var resultSection = document.getElementById('result-section');
            if (editorSection.style.display === 'none') {
                editorSection.style.display = 'block';
                resultSection.style.display = 'block';
                this.querySelector('img').src = '../static/icons/minimizar.png';
            } else {
                editorSection.style.display = 'none';
                resultSection.style.display = 'none';
                this.querySelector('img').src = '../static/icons/maximizar.png';
            }
        });

        document.getElementById('close-btn').addEventListener('click', function () {
            var edictCode = document.getElementById('edict-code');
            edictCode.style.display = 'none';
        });
        document.getElementById('execute-btn').addEventListener('click', function () {
            document.getElementById('code-form').submit();
        });
        // Inicializa los números de línea
        updateLineNumbers();