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
 * Copyright (c) 2018, Oracle and/or its affiliates. All rights reserved.
 */
package org.opengrok.indexer.history;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import org.junit.AfterClass;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;

import org.junit.BeforeClass;
import org.junit.Test;
import org.opengrok.indexer.condition.ConditionalRun;
import org.opengrok.indexer.condition.RepositoryInstalled;
import org.opengrok.indexer.configuration.RuntimeEnvironment;
import org.opengrok.indexer.util.ForbiddenSymlinkException;
import org.opengrok.indexer.util.TestRepository;

/**
 * Test RepositoryFactory
 *
 * @author Vladimir Kotal
 */
public class RepositoryFactoryTest {
    private static TestRepository repository;
    
    @BeforeClass
    public static void setUpClass() throws Exception {
        repository = new TestRepository();
        repository.create(RepositoryFactory.class.getResourceAsStream("repositories.zip"));
    }
    
    @AfterClass
    public static void tearDown() {
        if (repository != null) {
            repository.destroy();
            repository = null;
        }
    }

    @ConditionalRun(RepositoryInstalled.MercurialInstalled.class)
    @Test
    public void testRepositoryMatchingSourceRoot() throws IllegalAccessException, InvocationTargetException,
            ForbiddenSymlinkException, InstantiationException, NoSuchMethodException, IOException {

        File root = new File(repository.getSourceRoot(), "mercurial");
        RuntimeEnvironment env = RuntimeEnvironment.getInstance();
        env.setSourceRoot(root.getAbsolutePath());
        env.setProjectsEnabled(true);
        assertNull(RepositoryFactory.getRepository(root));
    }

    /*
     * There is no conditional run based on whether given repository is installed because
     * this test is not supposed to have working Mercurial anyway.
     */
    private void testNotWorkingRepository(String repoPath, String propName)
            throws InstantiationException, IllegalAccessException, NoSuchMethodException, InvocationTargetException,
            IOException, ForbiddenSymlinkException {

        RuntimeEnvironment env = RuntimeEnvironment.getInstance();
        String origPropValue = System.setProperty(propName, "/foo/bar/nonexistent");
        File root = new File(repository.getSourceRoot(), repoPath);
        env.setSourceRoot(repository.getSourceRoot());
        Repository repo = RepositoryFactory.getRepository(root);
        if (origPropValue != null) {
            System.setProperty(propName, origPropValue);
        }
        assertFalse(repo.isWorking());
    }
    
    @Test
    public void testNotWorkingMercurialRepository()
            throws InstantiationException, IllegalAccessException, NoSuchMethodException, InvocationTargetException,
            IOException, ForbiddenSymlinkException {
        testNotWorkingRepository("mercurial", MercurialRepository.CMD_PROPERTY_KEY);
    }
    
    @Test
    public void testNotWorkingBitkeeperRepository()
            throws InstantiationException, IllegalAccessException, NoSuchMethodException, InvocationTargetException,
            IOException, ForbiddenSymlinkException {
        testNotWorkingRepository("bitkeeper", BitKeeperRepository.CMD_PROPERTY_KEY);
    }
}
