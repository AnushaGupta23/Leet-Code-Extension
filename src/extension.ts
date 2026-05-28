import * as vscode from 'vscode';
import * as path from 'path';
import { exec } from 'child_process';

export function activate(context: vscode.ExtensionContext) {

    console.log('LeetCode Helper Extension is now active!');

    // Command to open webview
    const disposable = vscode.commands.registerCommand(
        'extension.showWebview',
        () => {

            const panel = vscode.window.createWebviewPanel(
                'leetcodeHelper',
                'LeetCode Helper',
                vscode.ViewColumn.One,
                {
                    enableScripts: true
                }
            );

            panel.webview.html = getWebviewContent();

            panel.webview.onDidReceiveMessage(
                async (message) => {

                    switch (message.command) {

                        case 'loadProblem':

                            const slug = message.slug;

                            vscode.window.showInformationMessage(
                                `Loading problem: ${slug}`
                            );

                            runPythonScript(slug, context);

                            return;

                        case 'runTests':

                            runTests(context);

                            return;

                        case 'runPythonTests':

                            runPythonTests(context);

                            return;
                    }
                },
                undefined,
                context.subscriptions
            );
        }
    );

    context.subscriptions.push(disposable);
}

function runPythonScript(
    slug: string,
    context: vscode.ExtensionContext
) {

    const scriptPath = path.join(
        context.extensionPath,
        'src',
        'script.py'
    );

    exec(
        `python3 "${scriptPath}" --titleSlug "${slug}"`,
        (error, stdout, stderr) => {

            if (error) {
                vscode.window.showErrorMessage(
                    `Error: ${stderr}`
                );
                return;
            }

            vscode.window.showInformationMessage(
                'Problem loaded successfully!'
            );

            openFile(context);
        }
    );
}

async function openFile(
    context: vscode.ExtensionContext
) {

    const filePath = path.join(
        context.extensionPath,
        'testcases',
        'question.txt'
    );

    const doc = await vscode.workspace.openTextDocument(filePath);

    vscode.window.showTextDocument(doc);
}

function runTests(
    context: vscode.ExtensionContext
) {

    const cppPath = path.join(
        context.extensionPath,
        'testcases',
        'c++.cpp'
    );

    const pythonScriptPath = path.join(
        context.extensionPath,
        'src',
        'run_testcases.py'
    );

    const testCaseDir = path.join(
        context.extensionPath,
        'testcases'
    );

    exec(
        `python3 "${pythonScriptPath}" "${cppPath}" "${testCaseDir}"`,
        (error, stdout, stderr) => {

            if (error) {
                vscode.window.showErrorMessage(stderr);
                return;
            }

            vscode.window.showInformationMessage(stdout);
        }
    );
}

function runPythonTests(
    context: vscode.ExtensionContext
) {

    const pythonPath = path.join(
        context.extensionPath,
        'testcases',
        'python3.py'
    );

    const pythonScriptPath = path.join(
        context.extensionPath,
        'src',
        'run_testcases_py.py'
    );

    const testCaseDir = path.join(
        context.extensionPath,
        'testcases'
    );

    exec(
        `python3 "${pythonScriptPath}" "${pythonPath}" "${testCaseDir}"`,
        (error, stdout, stderr) => {

            if (error) {
                vscode.window.showErrorMessage(stderr);
                return;
            }

            vscode.window.showInformationMessage(stdout);
        }
    );
}

function getWebviewContent(): string {

    return `
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">

        <style>

            body {
                font-family: Arial, sans-serif;
                padding: 20px;
            }

            input {
                padding: 8px;
                width: 300px;
            }

            button {
                padding: 8px 12px;
                margin-left: 10px;
            }

        </style>
    </head>

    <body>

        <h1>LeetCode Problem Helper</h1>

        <input
            type="text"
            id="slug"
            placeholder="Enter problem slug (e.g. two-sum)"
        />

        <button onclick="loadProblem()">
            Load Problem
        </button>

        <br><br>

        <button onclick="runCppTests()">
            Run C++ Tests
        </button>

        <button onclick="runPythonTests()">
            Run Python Tests
        </button>

        <script>

            const vscode = acquireVsCodeApi();

            function loadProblem() {

                const slug =
                    document.getElementById('slug').value;

                vscode.postMessage({
                    command: 'loadProblem',
                    slug: slug
                });
            }

            function runCppTests() {

                vscode.postMessage({
                    command: 'runTests'
                });
            }

            function runPythonTests() {

                vscode.postMessage({
                    command: 'runPythonTests'
                });
            }

        </script>

    </body>

    </html>
    `;
}

export function deactivate() {}