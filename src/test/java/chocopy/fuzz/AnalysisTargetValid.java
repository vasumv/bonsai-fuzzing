package chocopy.fuzz;

import chocopy.common.astnodes.Program;
import chocopy.reference.RefAnalysis;
import chocopy.reference.RefParser;
import com.pholser.junit.quickcheck.From;
import edu.berkeley.cs.jqf.fuzz.Fuzz;
import edu.berkeley.cs.jqf.fuzz.JQF;
import org.junit.runner.RunWith;

import static org.junit.Assume.assumeFalse;

@RunWith(JQF.class)
public class AnalysisTargetValid {

    /** Entry point for running reference semantic analysis with Chocopy code generator */
    @Fuzz
    public void runAnalysisValid(@From(ChocoPySemanticGenerator.class) String code) {
        Program program = RefParser.process(code, false);
        assumeFalse(program.hasErrors());
        Program refTypedProgram = RefAnalysis.process(program);
        assumeFalse(refTypedProgram.hasErrors());
    }
}
