<%page args="composite"/>
${composite.name().lower()|pyname} = ${composite.name()|pyname}('${composite.name().lower()}')
