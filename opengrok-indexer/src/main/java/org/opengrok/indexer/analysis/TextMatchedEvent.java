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
 * Copyright (c) 2017, Chris Fraire <cfraire@me.com>.
 */

package org.opengrok.indexer.analysis;

/**
 * Represents an event raised when a symbol matcher matches a string that
 * would not be published as a symbol.
 */
public class TextMatchedEvent {

    private final Object source;
    private final String str;
    private final EmphasisHint hint;
    private final int start;
    private final int end;

    /**
     * Initializes an immutable instance of {@link TextMatchedEvent}.
     * @param source the event source
     * @param str the text string
     * @param start the text start position
     * @param end the text end position
     */
    public TextMatchedEvent(Object source, String str, int start, int end) {
        this(source, str, EmphasisHint.NONE, start, end);
    }

    /**
     * Initializes an immutable instance of {@link TextMatchedEvent}.
     * @param source the event source
     * @param str the text string
     * @param hint the text hint
     * @param start the text start position
     * @param end the text end position
     */
    public TextMatchedEvent(Object source, String str, EmphasisHint hint,
        int start, int end) {
        this.source = source;
        this.str = str;
        this.hint = hint;
        this.start = start;
        this.end = end;
    }

    /**
     * Gets the event source.
     * @return the initial value
     */
    public Object getSource() {
        return source;
    }

    /**
     * Gets the text string.
     * @return the initial value
     */
    public String getStr() {
        return str;
    }

    /**
     * Gets the text start position.
     * @return the initial value
     */
    public int getStart() {
        return start;
    }

    /**
     * Gets the text end position.
     * @return the initial value
     */
    public int getEnd() {
        return end;
    }

    /**
     * Gets the text hint.
     * @return the initial value
     */
    public EmphasisHint getHint() {
        return hint;
    }
}
