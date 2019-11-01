/*
 * The contents of this file are Copyright © 2003 Jayson Falkner made available
 * under free license: "All of the code from Servlets and JSP the J2EE Web Tier
 * is freely available. Additonally all of the code the book's code relies on
 * is also freely available. With the exception of Sun's Java Development Kit,
 * everything the book relies on is also open-source. You are encouraged to
 * look at, learn from, and use everything!"
 * Copyright © 2017, Chris Fraire <cfraire@me.com>.
 */

package org.opengrok.web;

import java.io.IOException;
import java.util.Enumeration;
import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletResponse;

public class ResponseHeaderFilter implements Filter {
    FilterConfig fc;

    @Override
    public void doFilter(ServletRequest req, ServletResponse res,
        FilterChain chain)
        throws IOException, ServletException {

        HttpServletResponse response = (HttpServletResponse) res;

        // set the provided HTTP response parameters
        for (Enumeration<String> e = fc.getInitParameterNames(); e.hasMoreElements();) {
            String headerName = e.nextElement();
            if (!response.containsHeader(headerName)) {
                response.addHeader(headerName, fc.getInitParameter(headerName));
            }
        }

        // pass the request/response on
        chain.doFilter(req, response);
    }

    @Override
    public void init(FilterConfig filterConfig) {
        this.fc = filterConfig;
    }

    @Override
    public void destroy() {
        this.fc = null;
    }
}
