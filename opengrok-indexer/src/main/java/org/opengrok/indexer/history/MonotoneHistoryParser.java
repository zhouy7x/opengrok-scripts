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
 * Copyright (c) 2009, 2019, Oracle and/or its affiliates. All rights reserved.
 * Portions Copyright (c) 2017, Chris Fraire <cfraire@me.com>.
 */
package org.opengrok.indexer.history;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.file.InvalidPathException;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.opengrok.indexer.configuration.RuntimeEnvironment;
import org.opengrok.indexer.logger.LoggerFactory;
import org.opengrok.indexer.util.Executor;
import org.opengrok.indexer.util.ForbiddenSymlinkException;

/**
 * Class used to parse the history log from Monotone.
 *
 * @author Trond Norbye
 */
class MonotoneHistoryParser implements Executor.StreamHandler {

    private static final Logger LOGGER = LoggerFactory.getLogger(MonotoneHistoryParser.class);

    private List<HistoryEntry> entries = new ArrayList<>(); //NOPMD
    private final MonotoneRepository repository;
    private final String mydir;

    MonotoneHistoryParser(MonotoneRepository repository) {
        this.repository = repository;
        mydir = repository.getDirectoryName() + File.separator;
    }

    /**
     * Parse the history for the specified file or directory. If a changeset is
     * specified, only return the history from the changeset right after the
     * specified one.
     *
     * @param file the file or directory to get history for
     * @param changeset the changeset right before the first one to fetch, or
     * {@code null} if all changesets should be fetched
     * @return history for the specified file or directory
     * @throws HistoryException if an error happens when parsing the history
     */
    History parse(File file, String changeset) throws HistoryException {
        try {
            Executor executor = repository.getHistoryLogExecutor(file, changeset);
            int status = executor.exec(true, this);

            if (status != 0) {
                throw new HistoryException("Failed to get history for: \"" +
                                           file.getAbsolutePath() + "\" Exit code: " + status);
            }
        } catch (IOException e) {
            throw new HistoryException("Failed to get history for: \"" +
                                       file.getAbsolutePath() + "\"", e);
        }

        return new History(entries);
    }

    /**
     * Process the output from the hg log command and insert the HistoryEntries
     * into the history field.
     *
     * @param input The output from the process
     * @throws java.io.IOException If an error occurs while reading the stream
     */
    @Override
    public void processStream(InputStream input) throws IOException {
        RuntimeEnvironment env = RuntimeEnvironment.getInstance();
        BufferedReader in = new BufferedReader(new InputStreamReader(input));
        String s;

        HistoryEntry entry = null;
        int state = 0;
        while ((s = in.readLine()) != null) {
            s = s.trim();
            // Later versions of monotone (such as 1.0) output even more dashes so lets require
            // the minimum amount for maximum compatibility between monotone versions.
            if (s.startsWith("-----------------------------------------------------------------")) {
                if (entry != null && state > 2) {
                    entries.add(entry);
                }
                entry = new HistoryEntry();
                entry.setActive(true);
                state = 0;

                continue;
            }

            switch (state) {
                case 0:
                    if (s.startsWith("Revision:")) {
                        String rev = s.substring("Revision:".length()).trim();
                        entry.setRevision(rev);
                        ++state;
                    }
                    break;
                case 1:
                    if (s.startsWith("Author:")) {
                        entry.setAuthor(s.substring("Author:".length()).trim());
                        ++state;
                    }
                    break;
                case 2:
                    if (s.startsWith("Date:")) {
                        Date date = new Date();
                        try {
                            date = repository.parse(s.substring("date:".length()).trim());
                        } catch (ParseException pe) {
                            //
                            // Overriding processStream() thus need to comply with the
                            // set of exceptions it can throw.
                            //
                            throw new IOException("Could not parse date: " + s, pe);
                        }
                        entry.setDate(date);
                        ++state;
                    }
                    break;
                case 3:
                    if (s.startsWith("Modified ") || s.startsWith("Added ") || s.startsWith("Deleted ")) {
                        ++state;
                    } else if (s.equalsIgnoreCase("ChangeLog:")) {
                        state = 5;
                    }
                    break;
                case 4:
                    if (s.startsWith("Modified ") || s.startsWith("Added ") || s.startsWith("Deleted ")) {
                        continue;
                    } else if (s.equalsIgnoreCase("ChangeLog:")) {
                        state = 5;
                    } else {
                        String[] files = s.split(" ");
                        for (String f : files) {
                            File file = new File(mydir, f);
                            try {
                                String path = env.getPathRelativeToSourceRoot(
                                    file);
                                entry.addFile(path.intern());
                            } catch (ForbiddenSymlinkException e) {
                                LOGGER.log(Level.FINER, e.getMessage());
                                // ignore
                            } catch (FileNotFoundException e) { // NOPMD
                                // If the file is not located under the source root, ignore it
                            } catch (InvalidPathException e) {
                                LOGGER.log(Level.WARNING, e.getMessage());
                            }
                        }
                    }
                    break;
                case 5:
                    entry.appendMessage(s);
                    break;
                default:
                    LOGGER.warning("Unknown parser state: " + state);
                    break;
            }
        }

        if (entry != null && state > 2) {
            entries.add(entry);
        }
    }
}
