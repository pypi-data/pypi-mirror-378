<!--
  A stylesheet to confirm correct XPath behaviour.
  Run this with (eg) xsltproc against a sample XML input file

    -param with_element 1         :  include element name in the output
    -param path '//p[@a1="v2"]'   :  the XPath to search for
-->
<stylesheet xmlns='http://www.w3.org/1999/XSL/Transform'
            version='1.0'>

<output method='text'/>

<param name='with_element'/>
<param name='path' select='//p'/>

<template match="*">
  <text>[</text>
  <if test='$with_element'>
    <value-of select='name()'/>
    <text>, {</text>
    <for-each select="@*"><value-of select='name()'/>: <apply-templates/><if test='not(position()=last())'>, </if></for-each>
    <text>}, </text>
  </if>
  <apply-templates/>
  <choose>
    <when test='position()=last()'>]</when>
    <otherwise>], </otherwise>
  </choose>
</template>

<template match='/'>
  <for-each select='$path'>
    <apply-templates select='.'/>
    <text>&#x0a;</text>
  </for-each>
</template>

</stylesheet>
