const usernameInput = document.getElementById('username');
const userAvalaibility = document.getElementById('avaliabilityStatus')
let timeout = null;

usernameInput.addEventListener('input',async function(){
    const user = usernameInput.value;
    
    if (user.length < 5) {
        userAvalaibility.innerHTML = `<span style="color: grey;">Type at least 5 characters</span>`;
        clearTimeout(timeout); 
        return;
    }

    clearTimeout(timeout); // Annule le délai précédent
    timeout = setTimeout(async () => {
        try {
            const response = await fetch(`/checkUserAvaliability?username=${encodeURIComponent(user)}`);
            console.log('API Response Status:', response.status);
            const isAvailable = await response.json();
        
                if (isAvailable.available){
                    userAvalaibility.innerHTML = `<span style="color: green;">User is available</span>`;
                }else{
                    userAvalaibility.innerHTML = `<span style="color : red">User in use</span>`
                } ;
            } catch (error) {
                console.error('Error:', error);
                alert('Error checking users. Please try again.');
            }
        }, 300);
});