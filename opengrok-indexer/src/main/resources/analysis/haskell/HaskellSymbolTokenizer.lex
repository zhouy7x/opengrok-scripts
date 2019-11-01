/*
 * CDDL HEADER START
 *
 * The contents of this file are subject to the terms of the
 * Common Development and Distribution License (the "License").
 * You may not use this file except in compliance with the License.
 *
 * See LICENSE.txt included in this distribution for the specific
 * language governing permissions and limitations under the License.
 *
 * When distributing Covered Code, include this CDDL HEADER in each
 * file and include the License file at LICENSE.txt.
 * If applicable, add the following below this CDDL HEADER, with the
 * fields enclosed by brackets "[]" replaced with your own identifying
 * information: Portions Copyright [yyyy] [name of copyright owner]
 *
 * CDDL HEADER END
 */

/*
 * Copyright (c) 2015, 2018 Oracle and/or its affiliates. All rights reserved.
 * Portions Copyright (c) 2017, Chris Fraire <cfraire@me.com>.
 */

/*
 * Get Haskell symbols
 */

package org.opengrok.indexer.analysis.haskell;

import java.io.IOException;
import org.opengrok.indexer.analysis.JFlexSymbolMatcher;

/**
 * @author Harry Pan
 */
%%
%public
%class HaskellSymbolTokenizer
%extends JFlexSymbolMatcher
%unicode
%init{
    yyline = 1;
%init}
%int
%include CommonLexer.lexh
%char
%{
    private int nestedComment;

    public void reset() {
        super.reset();
        nestedComment = 0;
    }
%}

%state STRING CHAR COMMENT BCOMMENT

%include Common.lexh
%include Haskell.lexh
%%

<YYINITIAL> {
    {Identifier} {
        String id = yytext();
        if (!Consts.kwd.contains(id)) {
            onSymbolMatched(id, yychar);
            return yystate();
        }
    }
    {Number}    {}
    \"   { yybegin(STRING);   }
    \'   { yybegin(CHAR);     }
    "--" { yybegin(COMMENT);  }

    {NotComments}    {}
}

<STRING> {
    \\[\"\\]    {}
    \"   { yybegin(YYINITIAL); }
}

<CHAR> {    // we don't need to consider the case where prime is part of an identifier since it is handled above
    \\[\'\\]    {}
    \'   { yybegin(YYINITIAL); }
}

<COMMENT> {
    {EOL}    { yybegin(YYINITIAL); }
}

<YYINITIAL, BCOMMENT> {
    "{-"    {
        if (nestedComment++ == 0) {
            yybegin(BCOMMENT);
        }
    }
}

<BCOMMENT> {
    "-}"    {
        if (--nestedComment == 0) {
            yybegin(YYINITIAL);
        }
    }
}

// fallback
{WhspChar}+ |
[^] {}
