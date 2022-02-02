<%page args="composite"/>
${composite.name().lower()|pyname} = ${composite.name().capitalize()|pyname}_Composite('${composite.name().lower()}')
