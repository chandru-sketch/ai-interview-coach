function speakText(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 1;
        // Change the voice to a more natural or different AI voice
        const voices = window.speechSynthesis.getVoices();
        // Try to pick a more natural or female voice, fallback to first
        utterance.voice = voices.find(v => v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('natural')) || voices[0];
         window.speechSynthesis.speak(utterance);
    }
}
