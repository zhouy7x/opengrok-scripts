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
  * Copyright (c) 2006, 2018, Oracle and/or its affiliates. All rights reserved.
  */

package org.opengrok.indexer.util;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.opengrok.indexer.configuration.RuntimeEnvironment;
import org.opengrok.indexer.web.Statistics;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.Reader;

public class StatisticsUtils {
    /**
     * Dump statistics in JSON format into the file specified in configuration.
     *
     * @throws IOException I/O
     */
    public static void saveStatistics() throws IOException {
        String path = RuntimeEnvironment.getInstance().getStatisticsFilePath();
        if (path == null) {
            throw new FileNotFoundException("Statistics file is not set (null)");
        }
        saveStatistics(new File(path));
    }

    /**
     * Dump statistics in JSON format into a file.
     *
     * @param out the output file
     * @throws IOException I/O
     */
    public static void saveStatistics(File out) throws IOException {
        if (out == null) {
            throw new FileNotFoundException("Statistics file is not set (null)");
        }
        try (FileOutputStream ofstream = new FileOutputStream(out)) {
            saveStatistics(ofstream);
        }
    }

    /**
     * Dump statistics in JSON format into an output stream.
     *
     * @param out the output stream
     * @throws IOException I/O
     */
    public static void saveStatistics(OutputStream out) throws IOException {
        out.write(RuntimeEnvironment.getInstance().getStatistics().toJson().getBytes());
    }

    /**
     * Load statistics from JSON file specified in configuration.
     *
     * @throws IOException I/O
     */
    public static void loadStatistics() throws IOException {
        String path = RuntimeEnvironment.getInstance().getStatisticsFilePath();
        if (path == null) {
            throw new FileNotFoundException("Statistics file is not set (null)");
        }
        loadStatistics(new File(path));
    }

    /**
     * Load statistics from JSON file.
     *
     * @param in the file with json
     * @throws IOException I/O
     */
    public static void loadStatistics(File in) throws IOException {
        if (in == null) {
            throw new FileNotFoundException("Statistics file is not set (null)");
        }
        try (FileInputStream ifstream = new FileInputStream(in)) {
            loadStatistics(ifstream);
        }
    }

    /**
     * Load statistics from an input stream.
     *
     * @param in the file with json
     * @throws IOException I/O
     */
    public static void loadStatistics(InputStream in) throws IOException {
        try (Reader iReader = new InputStreamReader(in, "UTF-8")) {
            StringBuilder outputString = new StringBuilder();
            final char[] buf = new char[1024];
            int rsz;
            while ((rsz = iReader.read(buf, 0, buf.length)) > 0) {
                outputString.append(buf, 0, rsz);
            }

            ObjectMapper mapper = new ObjectMapper();
            org.opengrok.indexer.web.Statistics newstats = mapper.readValue(outputString.toString(), Statistics.class);
            RuntimeEnvironment.getInstance().setStatistics(newstats);
        }
    }

    private StatisticsUtils() {
        // private to ensure static
    }
}
