document.querySelectorAll('[data-yaday-play]').forEach(function(button){
  button.addEventListener('click',function(){
    var stage=button.closest('.yaday-video-stage');
    var status=stage.parentElement.querySelector('.yaday-video-status');
    if(button.dataset.yadayPlay==='film'){
      var video=stage.querySelector('video');
      video.style.display='block';
      var cover=stage.querySelector('.yaday-film-cover');
      cover.style.display='none';
      if(!video.getAttribute('src'))video.src='/assets/yaday/film-20261013.mp4';
      button.hidden=true;
      button.style.display='none';
      video.play().catch(function(){
        video.style.display='none';
        cover.style.display='';
        button.hidden=false;
        button.style.display='';
        status.textContent='La lecture n’a pas démarré. Réessayez ou ouvrez le film original.';
      });
    }else{
      var iframe=document.createElement('iframe');
      iframe.src='https://www.youtube-nocookie.com/embed/d9gdmn_hTcM?autoplay=1&rel=0';
      iframe.title='Yaday : In their own words';
      iframe.allow='accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; fullscreen';
      iframe.setAttribute('allowfullscreen','');
      iframe.referrerPolicy='strict-origin-when-cross-origin';
      stage.replaceChildren(iframe);
    }
  });
});
