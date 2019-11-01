<%--
CDDL HEADER START

The contents of this file are subject to the terms of the
Common Development and Distribution License (the "License").
You may not use this file except in compliance with the License.

See LICENSE.txt included in this distribution for the specific
language governing permissions and limitations under the License.

When distributing Covered Code, include this CDDL HEADER in each
file and include the License file at LICENSE.txt.
If applicable, add the following below this CDDL HEADER, with the
fields enclosed by brackets "[]" replaced with your own identifying
information: Portions Copyright [yyyy] [name of copyright owner]

CDDL HEADER END

Copyright (c) 2017, Oracle and/or its affiliates. All rights reserved.
Portions Copyright (c) 2018, Chris Fraire <cfraire@me.com>.
--%>
<%@page  session="false" import="org.opengrok.indexer.web.PageConfig" %>
<%
/* ---------------------- eforbidden.jspf start --------------------- */
{
    response.setStatus(HttpServletResponse.SC_FORBIDDEN);
%>
<%= PageConfig.get(request).getEnv().getIncludeFiles().getForbiddenIncludeFileContent(false) %>
<%
}
/* ---------------------- eforbidden.jspf end --------------------- */
%>
