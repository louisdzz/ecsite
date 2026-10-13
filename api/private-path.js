module.exports = function(req,res){res.setHeader('Cache-Control','no-store');res.setHeader('X-Robots-Tag','noindex');res.status(404).end('Page introuvable.');};
